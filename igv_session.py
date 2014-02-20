sessionXml ="""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<Session genome="hg19" hasGeneTrack="true" hasSequenceTrack="true" locus="{{chr}}:{{start_bp}}-{{stop_bp}}" version="8">
    <Resources>
        <Resource path="http://clinical-db:8082/static/99-2-1U/mosaik/GATK/99-2-1U.130815_BD26W2ACXX_indexAATGTTGC.lane5_sorted_pmd_rreal_brecal_reduced.bam"/>
        <Resource path="http://clinical-db:8082/static/99-2-2U/mosaik/GATK/99-2-2U.130815_BD26W2ACXX_indexAATCCGTC.lane4_sorted_pmd_rreal_brecal_reduced.bam"/>
        <Resource path="http://clinical-db:8082/static/99/mosaik/GATK/99_sorted_pmd_rreal_brecal_reduced_vrecal_BOTH.vcf"/>
    </Resources>
    <Panel height="96" name="DataPanel" width="1131">
        <Track SQUISHED_ROW_HEIGHT="4" altColor="0,0,178" autoScale="false" clazz="org.broad.igv.track.FeatureTrack" color="0,0,178" colorMode="GENOTYPE" displayMode="EXPANDED" featureVisibilityWindow="1994000" fontSize="10" id="http://localhost:5000/api/v1/static/99_sorted_pmd_rreal_brecal_vrecal_BOTH.vcf" name="99_sorted_pmd_rreal_brecal_vrecal_BOTH.vcf" renderer="BASIC_FEATURE" sortable="false" visible="true" windowFunction="count"/>
    </Panel>
    <Panel height="6067" name="Panel1390472597613" width="1131">
        <Track altColor="0,0,178" autoScale="true" color="175,175,175" colorScale="ContinuousColorScale;0.0;10.0;255,255,255;175,175,175" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10" id="http://localhost:5000/api/v1/static/99-1-1A.130815_BD26W2ACXX_indexAAGGACAC.lane4_sorted_pmd.bam_coverage" name="99-1-1A.130815_BD26W2ACXX_indexAAGGACAC.lane4_sorted_pmd.bam Coverage" showReference="false" snpThreshold="0.2" sortable="true" visible="true">
            <DataRange baseline="0.0" drawBaseline="false" flipAxis="false" maximum="10.0" minimum="0.0" type="LINEAR"/>
        </Track>
        <Track altColor="0,0,178" autoScale="false" color="0,0,178" displayMode="EXPANDED" featureVisibilityWindow="-1" fontSize="10" id="http://localhost:5000/api/v1/static/99-1-1A.130815_BD26W2ACXX_indexAAGGACAC.lane4_sorted_pmd.bam" name="99-1-1A.130815_BD26W2ACXX_indexAAGGACAC.lane4_sorted_pmd.bam" showSpliceJunctions="false" sortable="true" visible="true">
            <RenderOptions colorByTag="" colorOption="UNEXPECTED_PAIR" flagUnmappedPairs="false" groupByTag="" maxInsertSize="1000" minInsertSize="50" shadeBasesOption="QUALITY" shadeCenters="true" showAllBases="false" sortByTag=""/>
        </Track>
    </Panel>
    <Panel height="65" name="FeaturePanel" width="1131">
        <Track altColor="0,0,178" autoScale="false" color="0,0,178" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10" id="Reference sequence" name="Reference sequence" sortable="false" visible="true"/>
        <Track altColor="0,0,178" autoScale="false" clazz="org.broad.igv.track.FeatureTrack" color="0,0,178" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10" height="35" id="hg19_genes" name="RefSeq Genes" renderer="BASIC_FEATURE" sortable="false" visible="true" windowFunction="count"/>
    </Panel>
    <PanelLayout dividerFractions="0.166383701188455,0.8811544991511036"/>
    <HiddenAttributes>
        <Attribute name="NAME"/>
        <Attribute name="DATA FILE"/>
        <Attribute name="DATA TYPE"/>
    </HiddenAttributes>
</Session>
"""
