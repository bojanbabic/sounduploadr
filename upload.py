#!/usr/bin/python
import os, time, logging, random

import tornado.httpserver
import tornado.ioloop
import tornado.web

from hashlib import sha1
from hmac import new as hmac

AWS_ACCESS_KEY='AKIAJ5TKKYN3Q7BPXCBQ'
AWS_SECRET_KEY='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'
BUCKET_NAME='soundcloudr'
BUCKET_URI='https://s3-eu-west-1.amazonaws.com/soundcloudr/'

class MainHandler(tornado.web.RequestHandler):
        def get(self):
                self.set_header('Content-Type', 'text/html')
                #self.render("templates/upload.html.cp.1", title="Uplaod test" , data= [])
                self.render("index.html", title="Uplaod test" , data= [])
class UploadHandler(tornado.web.RequestHandler):
        def post(self):
                title = self.get_argument('title', default=None)
                self.set_header('Content-Type', 'text/html')
                title = self.get_argument('title', 'burning up inside')
                progressID = self.get_argument('X-Progress-ID' , default=None)
                filename = self.get_argument('media_file.name', default=None)
                path = self.get_argument('media_file.path', default=None)
                size = self.get_argument('media_file.size', default=None)
                signal = self.get_argument('signal', default=None)
                self.write('message:%s<br>' % title)
                self.write('filename %s<br>' % filename)
                self.write('path %s<br>' % path)
                self.write('progressID%s<br>' % progressID)
                self.write('size %s<br>' % size) 
        def get(self):
                title = self.get_argument('title', 'burning up inside')
                signal = self.get_argument('signal', default=None)
                self.write('title:%s<br>' % title)
                self.write('signal:%s<br>' % signal)
                filename='test.png'
                filedir='/tmp'
                
                fileNameS3=self.transferS3FromFile(filename, filedir)
                titleNameS3=self.transferS3FromString(title)
                if fileNameS3 is not None:
                        self.write(BUCKET_URI+fileNameS3)
                else:
                        self.write('hm something got wrong with file transfer')

        def savefile(self, filename, body):
                fn = os.path.basename("%s_%s" %(filename,str(int(time.time()))))
                open('files/'+ fn, 'wb').write(body)
                #logging.info('file %s have been uploaded to server' % on)

        def transferS3FromFile(self, filename, filedir):
                k = self.getBucketKey()
                k.key=filename+'_'+Util.getHash()
                k.set_contents_from_filename(filedir+'/'+filename)
                k.set_acl('public-read')

                return k.key

        def transferS3FromString(self, title):
                k = self.getBucketKey()
                k.key='title_'+Util.getHash()
                k.set_contents_from_string(title)
                k.set_acl('public-read')

                return k.key

        def getBucketKey(self):
                from boto.s3.connection import S3Connection
                conn=S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
                b = conn.get_bucket(BUCKET_NAME)
                from boto.s3.key import Key
                k = Key(b)
                return k

               
               
class Util:
        @staticmethod
        def getHash():
                now_str = str(int(time.time()))
                rnd_str = str(random.randrange(0,1000))

                hash_str = str(hash(str(now_str + '_' + rnd_str )))
                return hash_str[1:]


settings = {'static_path': os.path.join(os.path.dirname(__file__), "static")}
application=tornado.web.Application([
                        (r"/", MainHandler),
                        (r"/uload", UploadHandler),
                        ], **settings)

if __name__ == "__main__":
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
