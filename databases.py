import tornado.template as template
import tornado.httpserver
import tornado.ioloop
import tornado.escape
import tornado.web
import tornado.options
import logging
import clinic as clinic

tornado.log.enable_pretty_logging()
logging.getLogger().setLevel(logging.DEBUG)

application = tornado.web.Application([
    (r"/noInst", clinic.noInstitute),
    (r"/(favicon\.ico)", tornado.web.StaticFileHandler, {"path": "html"}),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "html"}),
    (r"/families(/?)", clinic.families),
    (r"/families/(?P<family>[^\/]+)?/?", clinic.getFamily),
    (r"/families/(?P<family>[^\/]+)?/comments", clinic.familyLog),
    (r"/families/(?P<family>[^\/]+)/(?P<database>[A-Za-z]+)", clinic.getFamilyDatabase),
    (r"/variants/(?P<variant>[\d]+)/gtcall", clinic.getVariantGtCall),
    (r"/variants/(?P<variant>[\d]+)", clinic.getVariant),
    (r"/variants/(?P<variant>[\d]+)/comments", clinic.getVariantComment),
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
