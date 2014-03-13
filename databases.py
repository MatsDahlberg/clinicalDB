import tornado.template as template
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import logging
import clinic as clinic

tornado.log.enable_pretty_logging()
logging.getLogger().setLevel(logging.DEBUG)

application = tornado.web.Application([
    (r"/noInst", clinic.noInstitute),
    (r"/(favicon\.ico)", tornado.web.StaticFileHandler, {"path": "html"}),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    (r"/families(/?)", clinic.families),
    (r"/families/(?P<family>[^\/]+)?/?", clinic.getFamily),
    (r"/families/(?P<family>[^\/]+)?/variants", clinic.getFamilyDatabase),
    (r"/families/(?P<family>[^\/]+)?/comments/?(?P<pk>[0-9]+)?", clinic.familyLog),
    (r"/families/(?P<family>[^\/]+)?/filter", clinic.familyFilter),
    (r"/variants/(?P<variant>[\d]+)/gtcall", clinic.getVariantGtCall),
    (r"/variants/(?P<variant>[\d]+)/compounds", clinic.getCompounds),
    (r"/variants/(?P<variant>[\d]+)/igv.xml", clinic.launchVariantIGV),
    (r"/variants/(?P<variant>[\d]+)", clinic.getVariant),
    (r"/compounds/(?P<variant>[\d]+)", clinic.getCompounds),
    (r"/variants/(?P<variant>[\d]+)/comments/?(?P<pk>[0-9]+)?", clinic.getVariantComment),
    (r"/compounds(.*)", clinic.getCompounds),
    (r"/gtcalls(.*)", clinic.getVariantGtCall),
    (r"/other_families(.*)", clinic.getOtherFamilies),
    (r"/other_families/(?P<variant>[\d]+)", clinic.getOtherFamilies),
    (r"/omim/(?P<gene>[^\/]+)?/?", clinic.omim),
    (r"/api", clinic.api),
    (r"/geneInfo(.*)", clinic.geneInfo),
    (r"/checkEmail/(?P<email>[^\/]+)", clinic.checkEmail),    
    (r"/getRegion(.*)", clinic.getRegion),
    (r"(.*)", clinic.fourOfour),],
                                      cookie_secret="31oETzKXQAGaYdkL9gEmGeJJFuYh7EQnp1XdTP1o/Vo=",
                                      login_url="/login", debug=True)


if __name__ == "__main__":
    application.listen(8082)
    tornado.ioloop.IOLoop.instance().start()
