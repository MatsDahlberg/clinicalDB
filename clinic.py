import tornado.template as template
import tornado.gen
import torndb as database
import common as common
import json
import tornado.auth as auth
import tornado.httpclient as httpclient
import ast
import datetime
import credentials as cred
import igv_session
import OMIMkey

db = database.Connection(cred.mysqlHost,
                         cred.mysqlDb,
                         user=cred.mysqlUser,
                         password=cred.mysqlPw)

class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.set_header("Cache-Control", "max-age=36000")
        sInst = checkLogin(self, False)
        if sInst == "" or sInst == None or sInst == 'None':
            common.DBG("No institute, redirecting to error")
            self.redirect('/noInst')
        self.sInst = sInst

def getFamilyAttributes(tFamily):
    tRes = []
    for iRow in range(len(tFamily)):
        sSqlTmp = """select distinct(g.gene_model) gene_model from clinical.variant v,
                    clinical.gene_model g where family='%s' and g.variantid = v.pk
                    order by gene_model""" % (tFamily[iRow].family)
        tGm = db.query(sSqlTmp)
        tGmRes = []
        for iGm in range(len(tGm)):
            tGmRes.append({tGm[iGm].gene_model:iGm})
            
        sSqlTmp = """select distinct(functional_annotation) functional_annotation from
                    clinical.variant where family = '%s' order by functional_annotation
                    """ % (tFamily[iRow].family)
        tFa = db.query(sSqlTmp)
        tFaRes = []
        for iFa in range(len(tFa)):
            tFaRes.append({tFa[iFa].functional_annotation:iFa})
            
        sSqlTmp = """select distinct(g.gene_annotation) gene_annotation from clinical.variant v,
                  clinical.gene_annotation g where family = '%s' and g.variantid = v.pk
                  order by gene_annotation """ % (tFamily[iRow].family)
        tGa = db.query(sSqlTmp)
        tGaRes = []
        for iGa in range(len(tGa)):
            tGaRes.append({tGa[iGa].gene_annotation:iGa})

        return {'id':tFamily[iRow].family,
                'clinical_db_gene_annotation':tFamily[iRow].database,
                'update_date':tFamily[iRow].ts.strftime('%Y-%m-%d'),
                'inheritence_models':tGmRes,
                'functional_annotations':tFaRes,
                'gene_annotations':tGaRes}

        tRes.append({'id':tFamily[iRow].family,
                     'clinical_db_gene_annotation':tFamily[iRow].iem,
                     'update_date':tFamily[iRow].ts.strftime('%Y-%m-%d'),
                     'inheritence_models':tGmRes,
                     'functional_annotations':tFaRes,
                     'gene_annotations':tGaRes})
    return tRes

def oneFamily(self, iFam):
    sSql = """select family, iem as 'database', DATE_FORMAT(ts, '%%Y-%%m-%%d') update_date
                  from clinical.family
                  where institute in """
    sSql += self.sInst + " and family= '" + iFam + "'"
    tFamily = db.query(sSql)
    sSql = """select idn, cmmsid, cmms_seqid, capture_date, capture_kit, capture_personnel, clinical_db, clustering_date,
              inheritance_model, isolation_date, isolation_kit, isolation_personnel, medical_doctor, phenotype, phenotype_terms,
              scilifeid, sequencing_kit, sex from clinical.patient where family = %s"""
    tSamples = db.query(sSql, iFam)

    tSamp = []
    for saSample in tSamples:
        tSamp.append(saSample)

    return {'id':iFam,
            'update_date':tFamily[0].update_date,
            'database':tFamily[0].database,
            'samples':tSamp}

def checkLogin(self, slask):
    sEmail = self.get_cookie("email")
    sInst = self.get_cookie("institute")
    #common.DBG(self.cookies)
    #common.DBG("Email: " + str(sEmail))
    sInst = str(sInst)
    if sInst == None or sInst == '""' or sInst == 'None':
        common.DBG("Error no institute: " + str(sInst))
        return None
    sInst = sInst.replace('"', '')
    saInst = sInst.split(',')
    instList = '('
    for i in range(len(saInst)):
        if i < len(saInst)-1:
            instList += "'" + str(saInst[i]) + "',"
        else:
            instList += "'" + str(saInst[i]) + "')"
    return instList

class fourOfour(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.set_status(404)
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(json.dumps({'Error':'404'}))

class getVariant(BaseHandler):
    def get(self, variant):
        sSql = """select v.pk,
        v.iem,
        rank_score,
        chr,
        ref_nt,
        alt_nt,
        start_bp,
        stop_bp,
        ensembl_geneid,
        hgmd,
        hgnc_symbol,
        pseudogene,
        v.gene_model gene_model,
        thousand_g,
        dbsnp129,
        dbsnp_id,
        dbsnp,
        dbsnp132,
        esp6500,
        disease_group,
        hgnc_approved_name,
        hgnc_synonyms,
        lrt_whole_exome,
        snorna_mirna_annotation,
        functional_annotation,
        location_reliability,
        omim_gene_desc,
        omim_morbid_desc,
        sift_whole_exome,
        gerp_element,
        phast_const_elements,
        main_location,
        other_location,
        phylop_whole_exome,
        expression_type,
        mutation_taster,
        genomic_super_dups,
        v.gene_annotation gene_annotation,
        gt_call_filter,
        polyphen_div_human,
        polyphen_var_human,
        gerp_whole_exome,
        disease_group,
        hbvdb,
        disease_gene_model,
        hgnc_transcript_id,
        IFNULL(max(rating), '') rating,
        variant_count
        from clinical.variant v inner join (clinical.gene_model as m, 
        clinical.gene_annotation as a, clinical.family f) on
        (v.pk=m.variantid and v.pk=a.variantid and v.family = f.family)
        left join clinical.variant_comment as c on
        (v.pk=c.variantid )
        where v.pk='%s' and f.institute in %s group by v.pk""" % (variant, self.sInst)

        tVariants = db.query(sSql)
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')

        if len(tVariants) == 0:
            self.set_status(406)            
            self.write(json.dumps({"Error":"Variant not found"}))
            return

        sSql = """select family, pk from clinical.variant where chr='%s' and start_bp='%s' and alt_nt='%s' and
               pk !=%s order by family""" % (tVariants[0].chr, tVariants[0].start_bp, tVariants[0].alt_nt, tVariants[0].pk)
        tOtherVariants = db.query(sSql)
        self.write(json.dumps(
                        {'id':tVariants[0].pk,
                         'clinical_db_gene_annotation':tVariants[0].iem,
                         'rank_score':tVariants[0].rank_score,
                         'chr':tVariants[0].chr,
                         'ref_nt':tVariants[0].ref_nt,
                         'alt_nt':tVariants[0].alt_nt,
                         'start_bp':tVariants[0].start_bp,
                         'stop_bp':tVariants[0].stop_bp,
                         'ensembl_geneid':tVariants[0].ensembl_geneid,
                         'hgmd':tVariants[0].hgmd,
                         'hgnc_symbol':tVariants[0].hgnc_symbol,
                         'pseudogene':tVariants[0].pseudogene,
                         'gene_model':tVariants[0].gene_model,
                         'thousand_g':tVariants[0].thousand_g,
                         'dbsnp129':tVariants[0].dbsnp129,
                         'dbsnp_id':tVariants[0].dbsnp_id,
                         'dbsnp':tVariants[0].dbsnp,
                         'dbsnp132':tVariants[0].dbsnp132,
                         'esp6500':tVariants[0].esp6500,
                         'disease_group':tVariants[0].disease_group,
                         'hgnc_approved_name':tVariants[0].hgnc_approved_name,
                         'hgnc_synonyms':tVariants[0].hgnc_synonyms,
                         'lrt_whole_exome':tVariants[0].lrt_whole_exome,
                         'snorna_mirna_annotation':tVariants[0].snorna_mirna_annotation,
                         'functional_annotation':tVariants[0].functional_annotation,
                         'location_reliability':tVariants[0].location_reliability,
                         'omim_gene_desc':tVariants[0].omim_gene_desc,
                         'omim_morbid_desc':tVariants[0].omim_morbid_desc,
                         'sift_whole_exome':tVariants[0].sift_whole_exome,
                         'gerp_element':tVariants[0].gerp_element,
                         'phast_const_elements':tVariants[0].phast_const_elements,
                         'main_location':tVariants[0].main_location,
                         'other_location':tVariants[0].other_location,
                         'phylop_whole_exome':tVariants[0].phylop_whole_exome,
                         'expression_type':tVariants[0].expression_type,
                         'mutation_taster':tVariants[0].mutation_taster,
                         'genomic_super_dups':tVariants[0].genomic_super_dups,
                         'gene_annotation':tVariants[0].gene_annotation,
                         'GT_call_filter':tVariants[0].gt_call_filter,
                         'polyphen_div_human':tVariants[0].polyphen_div_human,
                         'polyphen_var_human':tVariants[0].polyphen_var_human,
                         'gerp_whole_exome':tVariants[0].gerp_whole_exome,
                         'disease_group':tVariants[0].disease_group,
                         'hgnc_transcript_id':tVariants[0].hgnc_transcript_id,
                         'rating':tVariants[0].rating,
                         'disease_gene_model':tVariants[0].disease_gene_model,
                         'hbvdb':tVariants[0].hbvdb,
                         'variant_count':tVariants[0].variant_count,
                         'otherVariants':tOtherVariants}, indent=4))

class getFamilyDatabase(BaseHandler):
    def get(self, family):
        database = common.cleanInput(self.get_argument('database', ''))
        if database.upper() not in ('IEM', 'EP', 'RESEARCH'):
            return
        if database == 'RESEARCH':
            database = 'NO'
        sOffset = common.cleanInput(self.get_argument('offset', '0'))
        iOffset = int(sOffset)
            
        functionalSql = ""
        geneSql = ""
        inheritenceSql = ""
        functional_annotationsKeys = []
        gene_annotationsKeys = []
        inheritence_modelsKeys = []
        sRelationSql = ""
        sGeneNameSql = ""

        for key in sorted(self.request.arguments):
            if 'functional_annotations_' in key.lower():
                functional_annotationsKeys.append(" v.functional_annotation='" + key.lower().split('functional_annotations_')[1] + "' ")
            if 'gene_annotations_' in key.lower():
                gene_annotationsKeys.append(" a.gene_annotation='" + key.lower().split('gene_annotations_')[1] + "' ")
            if 'inheritence_models_' in key.lower():
                inheritence_modelsKeys.append(" m.gene_model='" + key.lower().split('inheritence_models_')[1] + "' ")
            if 'thousand_g' == key.lower() or 'dbsnp129' == key.lower() or 'dbsnp132' == key.lower() or 'esp6500' == key.lower():
                sKey = key.lower()
                
                sVal = common.cleanInput(self.get_argument(key))
                sRelation = common.cleanInput(self.get_argument('relation', None))
                if sRelation != None:
                    if sRelation == 'LESSER':
                        sRel = '<='
                    if sRelation == 'GREATER':
                        sRel = '>='
                    sRelationSql = " and (" + sKey + " " + sRel + " " + sVal + " or thousand_g is NULL)"
            if 'gene_name' == key.lower():
                sGeneNameSql = " and hgnc_symbol like '" + common.cleanInput(self.get_argument(key)) + "%%'"

        if len(functional_annotationsKeys) > 0:
            functionalSql = ' and (' + " or ".join(functional_annotationsKeys) + ')'
        if len(gene_annotationsKeys) > 0:
            geneSql = ' and (' + " or ".join(gene_annotationsKeys) + ')'
        if len(inheritence_modelsKeys) > 0:
            inheritenceSql = ' and (' + " or ".join(inheritence_modelsKeys) + ')'

        sSql = """select v.pk,
        v.iem,
        rank_score,
        chr,
        ref_nt,
        alt_nt,
        start_bp,
        stop_bp,
        ensembl_geneid,
        hgmd,
        hgnc_symbol,
        pseudogene,
        v.gene_model gene_model,
        thousand_g,
        dbsnp129,
        dbsnp_id,
        dbsnp,
        dbsnp132,
        esp6500,
        disease_group,
        hgnc_approved_name,
        hgnc_synonyms,
        lrt_whole_exome,
        snorna_mirna_annotation,
        functional_annotation,
        location_reliability,
        omim_gene_desc,
        omim_morbid_desc,
        sift_whole_exome,
        gerp_element,
        phast_const_elements,
        main_location,
        other_location,
        phylop_whole_exome,
        expression_type,
        mutation_taster,
        genomic_super_dups,
        v.gene_annotation gene_annotation,
        gt_call_filter,
        polyphen_div_human,
        polyphen_var_human,
        gerp_whole_exome,
        hbvdb,
        disease_gene_model,
        disease_group,
        hgnc_transcript_id,
        IFNULL(max(rating), '') rating,
        variant_count
        from clinical.variant v inner join (clinical.gene_model as m, 
        clinical.gene_annotation as a, clinical.family f) on
        (v.pk=m.variantid and v.pk=a.variantid and v.family = f.family)
        left join clinical.variant_comment as c on
        (v.pk=c.variantid )
        where v.iem='%s' and v.family='%s' and f.institute in %s
        """ % (database, family, self.sInst)
        sSql += inheritenceSql + geneSql + functionalSql + sRelationSql + sGeneNameSql
        sSql += " group by v.pk order by rank_score desc, pk LIMIT " + str(iOffset) + ',' + str(iOffset+100)

        tVariants = db.query(sSql)
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')
        tRes = []
        for iRow in range(len(tVariants)):
            tRes.append({'id':tVariants[iRow].pk,
                         'clinical_db_gene_annotation':tVariants[iRow].iem,
                         'rank_score':tVariants[iRow].rank_score,
                         'chr':tVariants[iRow].chr,
                         'ref_nt':tVariants[iRow].ref_nt,
                         'alt_nt':tVariants[iRow].alt_nt,
                         'start_bp':tVariants[iRow].start_bp,
                         'stop_bp':tVariants[iRow].stop_bp,
                         'ensembl_geneid':tVariants[iRow].ensembl_geneid,
                         'hgmd':tVariants[iRow].hgmd,
                         'hgnc_symbol':tVariants[iRow].hgnc_symbol,
                         'pseudogene':tVariants[iRow].pseudogene,
                         'gene_model':tVariants[iRow].gene_model,
                         'thousand_g':tVariants[iRow].thousand_g,
                         'dbsnp129':tVariants[iRow].dbsnp129,
                         'dbsnp_id':tVariants[iRow].dbsnp_id,
                         'dbsnp':tVariants[iRow].dbsnp,
                         'dbsnp132':tVariants[iRow].dbsnp132,
                         'esp6500':tVariants[iRow].esp6500,
                         'disease_group':tVariants[iRow].disease_group,
                         'hgnc_approved_name':tVariants[iRow].hgnc_approved_name,
                         'hgnc_synonyms':tVariants[iRow].hgnc_synonyms,
                         'lrt_whole_exome':tVariants[iRow].lrt_whole_exome,
                         'snorna_mirna_annotation':tVariants[iRow].snorna_mirna_annotation,
                         'functional_annotation':tVariants[iRow].functional_annotation,
                         'location_reliability':tVariants[iRow].location_reliability,
                         'omim_gene_desc':tVariants[iRow].omim_gene_desc,
                         'omim_morbid_desc':tVariants[iRow].omim_morbid_desc,
                         'sift_whole_exome':tVariants[iRow].sift_whole_exome,
                         'gerp_element':tVariants[iRow].gerp_element,
                         'phast_const_elements':tVariants[iRow].phast_const_elements,
                         'main_location':tVariants[iRow].main_location,
                         'other_location':tVariants[iRow].other_location,
                         'phylop_whole_exome':tVariants[iRow].phylop_whole_exome,
                         'expression_type':tVariants[iRow].expression_type,
                         'mutation_taster':tVariants[iRow].mutation_taster,
                         'genomic_super_dups':tVariants[iRow].genomic_super_dups,
                         'gene_annotation':tVariants[iRow].gene_annotation,
                         'GT_call_filter':tVariants[iRow].gt_call_filter,
                         'polyphen_div_human':tVariants[iRow].polyphen_div_human,
                         'polyphen_var_human':tVariants[iRow].polyphen_var_human,
                         'gerp_whole_exome':tVariants[iRow].gerp_whole_exome,
                         'disease_group':tVariants[iRow].disease_group,
                         'hgnc_transcript_id':tVariants[iRow].hgnc_transcript_id,
                         'rating':tVariants[iRow].rating,
                         'hbvdb':tVariants[iRow].hbvdb,
                         'disease_gene_model':tVariants[iRow].disease_gene_model,
                         'variant_count':tVariants[iRow].variant_count})
        self.write(json.dumps(tRes, indent=4))

class launchVariantIGV(tornado.web.RequestHandler):
    def get(self, variant):
        #self.set_header("Content-Type", "text/xml")
        tVariant = db.query("""select family, chr, (start_bp-100) as start_bp, (stop_bp+100) as stop_bp
                               from clinical.variant where pk='%s'""" % (variant))

        if len(tVariant) == 0:
            self.set_status(406)
            self.set_header("Content-Type", "application/json")
            self.set_header('Access-Control-Allow-Origin', '*')
            self.write(json.dumps({"Error":"Variant not found"}))
            return

        sBroad = "http://www.broadinstitute.org/igv/projects/current/igv.php?sessionURL="
        sDataFile = "https://clinical-db.scilifelab.se:8081/remote/static"
        sLocus = "&genome=hg19&locus=" + str(tVariant[0].chr) + ":" + str(tVariant[0].start_bp) + "-" + str(tVariant[0].stop_bp)

        tVcf = db.query("""select * from clinical.family where family='%s'""" % str(tVariant[0].family))
        sVcfFile = tVcf[0].vcf_file.replace('/mnt/hds/proj/cust003/analysis/exomes', '')
        sVcf = sDataFile + sVcfFile + ','

        sBamFiles = ""
        tPatient = db.query("""select bam_file from clinical.patient where family='%s' order by status""" % tVariant[0].family)
        for i in range(len(tPatient)):
            sBamFile = tPatient[i].bam_file.replace('/mnt/hds/proj/cust003/analysis/exomes', '')
            sBamFiles += sDataFile + sBamFile
            if i < len(tPatient)-1:
                sBamFiles += ','

        sRes = sBroad + sVcf + sBamFiles + sLocus
        self.redirect(sRes)

class getVariantGtCall(BaseHandler):
    def get(self, variant):
        tHgnc = db.query("""select hgnc_symbol, family, gene_model, ensembl_geneid from variant where pk='%s'""" % (variant))
        if len(tHgnc) == 0:
            return
        tVariants = []
        if "compound" in tHgnc[0].gene_model:
            tVariants = db.query("""select distinct(v.pk) vpk, rank_score, gene_model, group_concat(idn) idn, group_concat(gt) gt,
            gene_annotation, functional_annotation
            from clinical.variant v, clinical.variation_quality q where
            v.pk = q.variantid and family='%s' and ensembl_geneid like %s and gene_model like %s
            group by start_bp order by rank_score desc""" % (tHgnc[0].family, "'%%" + tHgnc[0].ensembl_geneid + "%%'", "'%%compound%%'"))
        tRes = db.query("""SELECT * from clinical.variation_quality where variantid ='%s' order by idn""" % variant)
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')
        cRes = {'GT':tRes,
                'COMPOUNDS':tVariants}
        if len(tRes) > 0:
            self.write(json.dumps(cRes, indent=4))

class getFamily(BaseHandler):
    def get(self, family):
        tRes = oneFamily(self, family)
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')
        #self.write(json.dumps(tFamily, indent=4))
        self.write(json.dumps(tRes, indent=4))

class familyFilter(BaseHandler):
    def get(self, family):
        tFamily = db.query("""select family, iem as 'database', pedigree, ts
                              from clinical.family
                              where institute in %s and family='%s'""" % (self.sInst, family))

        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')
        tRes = getFamilyAttributes(tFamily)
        self.write(json.dumps(tRes, indent=4))

class families(BaseHandler):
    def get(self, *args, **kwargs):
        tFamily = db.query("""select family from clinical.family
                              where institute in %s order by family *1""" % (self.sInst))

        tFamRes = []
        for i in range(len(tFamily)):
            tFamRes.append(oneFamily(self, tFamily[i].family))

        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(json.dumps(tFamRes, indent=4))
        return
        tRes = []
        for iRow in range(len(tFamily)):
            tRes.append({'id':tFamily[iRow].family,
                         'database':tFamily[iRow].iem,
                         'pedigree':tFamily[iRow].pedigree,
                         'update_date':tFamily[iRow].ts.strftime('%Y-%m-%d')})


class geneInfo(BaseHandler):
    def loggedin(self, sEnsg, sIem, sFamily):
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')

        if sFamily == "":
            tVariants = db.query("""select distinct(pk) pk from clinical.variant where
            iem='%s' and ensembl_geneid like %s order by rank_score desc, (gene_model = 'AR_compound;') desc
            """ % (sIem,  "'" + sEnsg + "%%'"))
        else:
            tVariants = db.query("""select distinct(pk) pk from clinical.variant where iem='%s' and
            ensembl_geneid like %s and family='%s' order by rank_score desc, (gene_model = 'AR_compound;') desc
            """ % (sIem, "'" + sEnsg + "%%'", sFamily))

        if len(tVariants) == 0:
            return {}
        variants = []
        for variant in tVariants:
            tVariant = db.query("""select hgnc_symbol, variantid, q.idn, filter, gt, ad, dp, pl, gq, start_bp,
                                  stop_bp, ref_nt, alt_nt, functional_annotation, gene_annotation, gene_model, rank_score
                                  FROM clinical.variation_quality q, clinical.variant v where iem='%s' and
                                  q.variantid = v.pk and v.pk='%s' order by idn""" % (sIem, variant.pk))
            entry = [{'variantid':tVariant[0].variantid,
                      'start_bp':tVariant[0].start_bp,
                      'stop_bp':tVariant[0].stop_bp,
                      'ref_nt':tVariant[0].ref_nt,
                      'alt_nt':tVariant[0].alt_nt,
                      'type':tVariant[0].gene_annotation,
                      'gene':tVariant[0].hgnc_symbol,
                      'rank_score':tVariant[0].rank_score,
                      'functional_annotation':tVariant[0].functional_annotation,
                      'gene_model':tVariant[0].gene_model}]
            family = []
            for patient in tVariant:
                family.append({'idn':patient.idn,
                               'ad':patient.ad,
                               'dp':patient.dp,
                               'gq':patient.gq,
                               'gt':patient.gt,
                               'pl':patient.pl,
                               'filter':patient.filter
                               })
            entry.append(family)
            variants.append(entry)

        tExons = db.query("""select start_bp, stop_bp, gene_start, gene_end, chromosome, exon_id
                  from clinical.gene2exon where ensg ='%s' order by start_bp""" % (sEnsg))
        tRes = []

        try:
            for exon in range(len(tExons)):
                tRes.append({'start_bp':tExons[exon].start_bp,
                             'stop_bp':tExons[exon].stop_bp,
                             'exon_id':tExons[exon].exon_id})

            self.write(json.dumps({'variants':variants,
                                   'exons':tRes,
                                   'gene_start':tExons[0].gene_start,
                                   'gene_end':tExons[0].gene_end,
                                   'chr':tExons[0].chromosome}, sort_keys=True, indent=4))
        except:
            pass

    def get(self, *args, **kwargs):
        sInput = self.my_get_argument('data')
        if sInput =="":
            return

        try:
            sIem = self.my_get_argument('type')
            if sIem not in ("IEM", "EP"):
                sIem = "NO"
        except Exception as e:
            common.DBG(str(e))
            sIem = "NO"
        try:
            sFamily = self.my_get_argument('family')
        except Exception as e:
            common.DBG(str(e))
            sFamily = ""
        self.loggedin(sInput, sIem, sFamily)

class getVariantComment(tornado.web.RequestHandler):
    def get(self, variant, pk='all'):
        sVariant = common.cleanInput(variant)
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')

        if pk=='all' or pk==None:
            sPkSql = ''
        else:
            sPkSql = 'and c.pk=' + str(pk)

        sSql = """SELECT c.pk, u.email, u.name user_name, DATE_FORMAT(created_date, '%%Y-%%m-%%d') created_date,
                  user_comment, rating, variantid FROM clinical.variant_comment c, clinical.users u
                  where c.user_pk = u.pk and variantid = %s """
        sSql += sPkSql + " order by created_date"

        tLog = db.query(sSql, sVariant)
        self.write(json.dumps(tLog, indent=4))

    def post(self, variant, pk='all'):
        sVariant = common.cleanInput(variant)
        try:
            data = ast.literal_eval(self.request.body)
            sEmail = data['email']
            sRating = data['rating']
            sComment = data['user_comment']
        except:
            self.set_status(406)
            self.write(json.dumps({"Error":"Malformed JSON input"}))
            return
        try:
            sInst = db.query("""select institute from clinical.family f, clinical.variant v
                           where f.family = v.family and v.pk='%s'""" % (sVariant))[0].institute
            sUserPk = db.query("""select pk from users where email ='%s' and institute='%s'
                           """  % (sEmail, sInst))[0].pk
        except:
            self.set_status(406)
            self.write(json.dumps({"Error":"Unknown email or institute, got: " + sInst + " " + sEmail}))
            return
            
        tCommentPk = db.query("""select pk from clinical.variant_comment where user_pk='%s' and variantid='%s'
                              """ % (sUserPk, sVariant))
        if len(tCommentPk) == 0:
            sSql = """insert into clinical.variant_comment (user_pk, created_date, user_comment, rating, variantid)
                      values (%s, now(), %s, %s, %s)"""
            db.execute(sSql, sUserPk, sComment, sRating, sVariant)
            tPk = db.query("""select pk from clinical.variant_comment where user_pk='%s' and variantid='%s'
                              """ % (sUserPk, sVariant))
            pk = tPk[0].pk
        else:
            sSql = """update clinical.variant_comment set user_pk=%s, created_date=now(),
                      user_comment=%s, rating=%s, variantid=%s where pk=%s"""
            db.execute(sSql, sUserPk, sComment, sRating, sVariant, tCommentPk[0].pk)
            pk = tCommentPk[0].pk
        self.get(sVariant, pk)

    def put(self, variant, pk='all'):
        self.post(variant, pk)

    def delete(self, variant, pk):
        sVariant = common.cleanInput(variant)
        sPk = common.cleanInput(pk)

        sSql = """delete from clinical.variant_comment where pk=%s"""
        tRes = db.execute(sSql, sPk)
        self.get(sVariant)

class familyLog(tornado.web.RequestHandler):
    def get(self, family, pk='all'):
        sFamily = common.cleanInput(family)
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')

        if pk=='all' or pk==None:
            sPkSql = ''
        else:
            sPkSql = 'and l.pk=' + str(pk)
        tFam = db.query("""select institute from clinical.family where family='%s'""" % (sFamily))
        sSql = """select l.pk, u.name user_name, u.email, l.family, log_column,
                  DATE_FORMAT(created_date, '%%Y-%%m-%%d') created_date,
                  position_in_column, user_comment from clinical.users u, clinical.family_log l
                  where u.institute=%s and u.email=l.email and family=%s"""
        sSql += sPkSql + " order by created_date"
        tLog = db.query(sSql, tFam[0].institute, sFamily)
        self.write(json.dumps(tLog, indent=4))

    def post(self, family, pk='all'):
        data = ast.literal_eval(self.request.body)
        try:
            sFamily = data['family']
            sEmail = data['email']
            sUserComment = data['user_comment']
            sLogColumn = data['log_column']
            sPositionInColumn = data['position_in_column']
        except:
            self.write(json.dumps({"Error":"Malformed JSON input"}))
            return
        sSql = """select pk from clinical.family_log where
                  email=%s and family=%s and log_column=%s and position_in_column=%s"""
        tRes = db.query(sSql, sEmail, sFamily, sLogColumn, sPositionInColumn)
        if len(tRes) == 0:
            sSql = """insert into clinical.family_log (email, family, log_column,
                      position_in_column, user_comment, created_date)
                      values (%s, %s, %s, %s, %s, now())"""
            db.execute(sSql, sEmail, sFamily, sLogColumn, sPositionInColumn, sUserComment)
            sSql = """select pk from clinical.family_log where
                      email=%s and family=%s and log_column=%s and position_in_column=%s"""
            db.query(sSql, sEmail, sFamily, sLogColumn, sPositionInColumn)
            tPk = db.query(sSql, sEmail, sFamily, sLogColumn, sPositionInColumn)
            pk = tPk[0].pk
        else:
            sSql = """update clinical.family_log
                      set email=%s, family=%s, log_column=%s, position_in_column=%s, user_comment=%s
                      where pk=%s"""
            pk = int(tRes[0].pk)
            db.execute(sSql, sEmail, sFamily, sLogColumn, sPositionInColumn, sUserComment, pk)
        self.get(sFamily, pk)

    def put(self, family, pk='all'):
        self.post(family, pk)

    def delete(self, family, pk):
        sPk = common.cleanInput(pk)
        sFamily = common.cleanInput(family)
        sSql = """delete from clinical.family_log where pk=%s"""
        tRes = db.execute(sSql, sPk)
        self.get(sFamily, sPk)

class getRegion(BaseHandler):
    def loggedin(self, sChr, sBpStart, sBpStop, sIem, sFamily):
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')

        tVariants = []
        tExons = []
        sChrStripped = sChr.replace("CHR", "")
        tGenes = db.query("""select gene_name, gene_start, gene_end, chromosome
                 from clinical.gene2exon where chromosome = '%s' and start_bp > '%s' and start_bp <'%s'
                 group by gene_name, gene_start, gene_end, chromosome order by start_bp""" % (sChrStripped, sBpStart, sBpStop))

        iMinStart = int(sBpStart)
        iMaxStop = int(sBpStop)
        for gene in tGenes:
            if iMinStart > gene.gene_start:
                iMinStart = gene.gene_start
            if iMaxStop < gene.gene_end:
                iMaxStop = gene.gene_end

        sBpStart = iMinStart
        sBpStop = iMaxStop

        # CNTNAP2 is the largest gene and is 2304637 bases long
        if int(sBpStop) - int(sBpStart) < 2404638000:
            tExons = db.query("""select start_bp, stop_bp, gene_start, gene_end, chromosome, exon_id
                                 from clinical.gene2exon where chromosome = '%s'
                                 and start_bp >= '%s' and start_bp <='%s' order by start_bp""" % (sChrStripped, sBpStart, sBpStop))

            if sFamily == "":
                tVariants = db.query("""select distinct(pk) pk from clinical.variant where
                iem='%s' and ensembl_geneid like %s order by rank_score desc,
                (gene_model = 'AR_compound;') desc""" % (sIem,  "'%%" + sEnsg + "%%'"))
            else:
                tVariants = db.query("""select distinct(pk) pk from clinical.variant where iem='%s' and
                chr = '%s' and family='%s' and start_bp > '%s' and stop_bp < '%s'
                order by rank_score desc
                """ % (sIem, sChr, sFamily, sBpStart, sBpStop))

        variants = []
        features = []
        tCov = db.query("""select features_passed, start_bp, stop_bp, idn,
                           fraction_coverage, group_concat(DISTINCT ' ',idn, ' ', fraction_coverage, ' ', features_passed) cov
                           from clinical.feature_coverage where clinical.feature_coverage.chr = '%s' and start_bp >%s and
                           stop_bp < %s and idn like %s group by start_bp""" % (sChr, sBpStart, sBpStop, "'" + sFamily + "-%%'"))
        for thisRow in tCov:
            features.append({'start_bp':thisRow.start_bp,
                             'stop_bp':thisRow.stop_bp,
                             'idn':thisRow.cov})

        for variant in tVariants:
            tVariant = db.query("""select hgnc_symbol, variantid, q.idn, filter, gt, ad, dp, pl, gq, start_bp,
                                  stop_bp, ref_nt, alt_nt, functional_annotation, gene_annotation, gene_model, rank_score
                                  FROM clinical.variation_quality q, clinical.variant v where
                                  q.variantid = v.pk and v.pk='%s' order by idn""" % (variant.pk))

            entry = [{'variantid':tVariant[0].variantid,
                      'start_bp':tVariant[0].start_bp,
                      'stop_bp':tVariant[0].stop_bp,
                      'ref_nt':tVariant[0].ref_nt,
                      'alt_nt':tVariant[0].alt_nt,
                      'type':tVariant[0].gene_annotation,
                      'rank_score':tVariant[0].rank_score,
                      'gene':tVariant[0].hgnc_symbol,
                      'functional_annotation':tVariant[0].functional_annotation,
                      'gene_model':tVariant[0].gene_model}]
            family = []
            for patient in tVariant:
                family.append({'idn':patient.idn,
                               'ad':patient.ad,
                               'dp':patient.dp,
                               'gq':patient.gq,
                               'gt':patient.gt,
                               'pl':patient.pl,
                               'filter':patient.filter
                               })
            entry.append(family)
            variants.append(entry)
        tRes = []
        cGenes = []
        try:
            for iGene in range(len(tGenes)):
                cGenes.append({'gene_name':tGenes[iGene].gene_name,
                               'gene_start':tGenes[iGene].gene_start,
                               'gene_end':tGenes[iGene].gene_end})
            for exon in range(len(tExons)):
                tRes.append({'start_bp':tExons[exon].start_bp,
                             'stop_bp':tExons[exon].stop_bp,
                             'exon_id':tExons[exon].exon_id})

            self.write(json.dumps({'variants':variants,
                                   'exons':tRes,
                                   'coverage':features,
                                   'genes':cGenes,
                                   'bp_start':sBpStart,
                                   'bp_end':sBpStop,
                                   'chr':sChrStripped}, sort_keys=True, indent=4))
        except Exception as e:
            common.DBG(str(e))

    def get(self, *args, **kwargs):
        try:
            sChr = self.get_argument('chr')
            sChr = common.cleanInput(sChr)
            sBpStart = self.get_argument('bp_start')
            sBpStart = common.cleanInput(sBpStart)
            sBpStop = self.get_argument('bp_stop')
            sBpStop = common.cleanInput(sBpStop)
        except Exception as e:
            common.DBG(e)
            return
        try:
            sIem = self.get_argument('type')
            sIem = common.cleanInput(sIem)
            if sIem not in ("IEM", "EP"):
                sIem = "NO"
        except Exception as e:
            common.DBG(str(e))
            sIem = "NO"
        try:
            sFamily = self.get_argument('family')
            sFamily = common.cleanInput(sFamily)
        except Exception as e:
            common.DBG(str(e))
            sFamily = ""
                
        self.loggedin(sChr, sBpStart, sBpStop, sIem, sFamily)

class omim(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, gene):
        oMimId = ""
        sOmimTitle = ""
        sChromosomeSymbol = ""
        nt_start = ""
        nt_stop = ""
        saSyndroms = ""

        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')
        sInput = gene
        client = httpclient.AsyncHTTPClient()

        sUrl = "http://api.europe.omim.org/api/entry/search?search=approved_gene_symbol:" + sInput + "&include=geneMap,allelicVariantList&format=python&apiKey=" + OMIMkey.OMIMkey
        response = yield tornado.gen.Task(client.fetch, sUrl)

        def parseAllelicVariantList(saVariants):
            saVariantNames = []
            for iVariant in range(len(saVariants)):
                sStatus =  saVariants[iVariant]['allelicVariant']['status']
                if sStatus == 'live':
                    saVariantNames.append(saVariants[iVariant]['allelicVariant']['name'])
            setVariant = set(saVariantNames)
            return list(setVariant)
        try:
            tt = ast.literal_eval(response.body)
            oMimId = tt['omim']['searchResponse']['entryList'][0]['entry']['mimNumber']
            oMimId = str(oMimId)
            sUrl = "http://api.europe.omim.org/api/entry?mimNumber=" + oMimId + "&format=python&include=geneMap,allelicVariantList&apiKey=" + OMIMkey.OMIMkey
            response = yield tornado.gen.Task(client.fetch, sUrl)

            tt = ast.literal_eval(response.body)
            ttt = tt['omim']['entryList'][0]
            sOmimTitle = ttt['entry']['titles']['preferredTitle']
            nt_start = ttt['entry']['geneMap']['chromosomeLocationStart']
            nt_stop = ttt['entry']['geneMap']['chromosomeLocationEnd']
            sChromosomeSymbol = ttt['entry']['geneMap']['chromosomeSymbol']
            saSyndroms = []
            if ttt['entry'].has_key('allelicVariantList'):
                saSyndroms = parseAllelicVariantList(ttt['entry']['allelicVariantList'])

            self.write(json.dumps({"OMIM_ID":oMimId,
                                   "OMIM_TITLE":sOmimTitle,
                                   "CHR":sChromosomeSymbol,
                                   "NT_START":nt_start,
                                   "NT_STOP":nt_stop,
                                   "SYNDROMS":saSyndroms}, sort_keys=True, indent=4))
        except Exception as e:
            self.write(json.dumps({"OMIM_ID":oMimId,
                                   "OMIM_TITLE":sOmimTitle,
                                   "CHR":sChromosomeSymbol,
                                   "NT_START":nt_start,
                                   "NT_STOP":nt_stop,
                                   "SYNDROMS":saSyndroms}, sort_keys=True, indent=4))
        self.finish()

class noInstitute(tornado.web.RequestHandler):
    def get(self):
        self.set_status(406)
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(json.dumps({"Error":"No institute"}))

class api(BaseHandler):
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')

        sFamilies = [{"Description":"Returns info of all families"},
                     {"Example":"http://clinical-db.scilifelab.se:8082/families"}]

        sOneFamily = [{"Description":"Meta data about one family"},
                      {"Example":"http://clinical-db.scilifelab.se:8082/families/1"}]

        sFamilyLog = [{"Description":"Log information about a family"},
                      {"Example":"http://clinical-db.scilifelab.se:8082/families/1/comments"}]

        sFirstVariants = [{"Description":"Returns the 200 first variants of a family. Database can be iem, ep or none."},
                          {"Example":"http://clinical-db.scilifelab.se:8082/families/1/iem"}]

        sOneVariant = [{"Description":"Returns data for a specific variant"},
                       {"Example":"http://clinical-db.scilifelab.se:8082/variants/2001982"}]

        sVariantComments = [{"Description":"Comments for a specific variant"},
                            {"Example":"http://clinical-db.scilifelab.se:8082/variants/2001982/comments"}]

        sVariantIgv = [{"Description":"Generates an XML file for launching IGV to investigate a variant"},
                       {"Example":"http://clinical-db.scilifelab.se:8082/variants/2001982/igv.xml"}]

        sGtCall = [{"Description":"GT-call data for a specific variant"},
                            {"Example":"http://clinical-db.scilifelab.se:8082/variants/1627432/gtcall"}]

        sOmim = [{"Description":"OMIM data for a gene"},
                 {"Example":"http://clinical-db.scilifelab.se:8082/omim/cdk2"}]

        sEmail = [{"Description":"Returns data about a user given their email-address"},
                  {"Example":"http://clinical-db.scilifelab.se:8082/checkEmail/mats.dahlberg@scilifelab.se"}]

        self.write(json.dumps([{"01. All families":sFamilies,
                               "02. One family data":sOneFamily,
                               "03. One family comments":sFamilyLog,
                               "04. Get 200 first variants for a family":sFirstVariants,
                               "05. Get 1 variant":sOneVariant,
                               "06. Get gt-call for a variant":sGtCall,
                               "07. Get comments for a variant":sVariantComments,
                               "08. Generate an XML-file for the IGV-browser":sVariantIgv,
                               "09. OMIM data for a gene":sOmim,
                               "10. Get user data":sEmail
                               }], sort_keys=True, indent=4))

class checkEmail(tornado.web.RequestHandler):
    def get(self, email):
        self.set_header("Content-Type", "application/json")
        self.set_header('Access-Control-Allow-Origin', '*')
        sEmail = common.cleanInput(email)
        sSql = "update clinical.users SET last_logon = now() where email = '" + sEmail +"' and pk >0 "
        slask = db.execute(sSql)
        tRes = db.query("select * from clinical.users where email = '%s'" % sEmail)
        if len(tRes) > 0:
            sInstitute = ''
            for iInst in range(len(tRes)):
                if iInst < len(tRes)-1:
                    sInstitute += str(tRes[iInst].institute) + ","
                else:
                    sInstitute += str(tRes[iInst].institute)

            cRes = {'email':str(tRes[0].email),
                    'institute':sInstitute,
                    'user_name':str(tRes[0].name)}
            self.set_cookie("institute", tornado.escape.json_encode(sInstitute))
            self.set_cookie("email", str(tRes[0].email))
            self.write(json.dumps(cRes, indent=4))
        else:
            self.set_cookie("institute", tornado.escape.json_encode(""))
            self.write(json.dumps({'Error':'Not a valid user'}, indent=4))
