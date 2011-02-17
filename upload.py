#!/usr/bin/python
import os, time, logging, random, urllib

import tornado.httpserver
import tornado.ioloop
import tornado.web

from hashlib import sha1
from hmac import new as hmac

AWS_ACCESS_KEY='AKIAJ5TKKYN3Q7BPXCBQ'
AWS_SECRET_KEY='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'
BUCKET_NAME='soundcloudr'
BUCKET_URI='https://s3-eu-west-1.amazonaws.com/soundcloudr/'
#TMP_FILE_STORAGE='/home/ec2-user/sounduploadr/tmp/'

class MainHandler(tornado.web.RequestHandler):
        def get(self):
                self.set_header('Content-Type', 'text/html')
                #self.render("templates/upload.html.cp.1", title="Uplaod test" , data= [])
                self.render("index.html", title="Upload test" , data= [])
class SendText(tornado.web.RequestHandler):
        def get(self):
                title = tornado.escape.utf8(self.get_argument('title', None))
                progressID = self.get_argument('X-Progress-ID', None)
                s3File = Util.transferS3FromString(title, progressID)

		hashProgressID = Util.getHash(progressID)
		fileUrl = BUCKET_URI + 'file_'+ hashProgressID
		titleUrl = BUCKET_URI + 'title_'+ hashProgressID
                self.write('title:%s<br>' % title)
                
                if s3File is not None:
			self.write("File saved:")
                        self.write("<a href=\"%s\">%s</a><br>" %(fileUrl ,fileUrl))
			self.write("Title '%s' saved:" % title)
                        self.write("<a href=\"%s\">%s</a>" %(titleUrl,titleUrl))
                else:
                        self.write('hm something got wrong with file transfer')

class UploadHandler(tornado.web.RequestHandler):
        def post(self):
                title = self.get_argument('title', default=None)
                self.set_header('Content-Type', 'text/html')
                progressID = self.get_argument('X-Progress-ID' , default=None)
                filename = self.get_argument('media_file.name', default=None)
                path = self.get_argument('media_file.path', default=None)
                size = self.get_argument('media_file.size', default=None)


                #fileNameS3=u.transferS3FromFile(path, TMP_FILE_STORAGE, progressID)
                fileNameS3=Util.transferS3FromFile(path, progressID)
                fileUrl = BUCKET_URI+fileNameS3

                self.write('message:%s<br>' % title)
                logging.error('message:%s<br>' % title)
                self.write('filename %s<br>' % filename)
                logging.error('filename %s<br>' % filename)
                self.write('path:%s<br>' % path)
                logging.error('path:%s<br>' % path)
                self.write('progressID:%s<br>' % progressID)
                logging.error('progressID:%s<br>' % progressID)
                self.write('size %s<br>' % size) 
                logging.error('size %s<br>' % size) 

               
class Util:
        @staticmethod
        def getHash(string):
                hash_str = str(hash(string))
                return hash_str[1:]

        @staticmethod
        def savefile(filename, body):
                fn = os.path.basename("%s_%s" %(filename,str(int(time.time()))))
                open('files/'+ fn, 'wb').write(body)
                #logging.info('file %s have been uploaded to server' % on)

        #def transferS3FromFile(self, filename, filedir, progressID):
        @staticmethod
        def transferS3FromFile(path, progressID):
                k = Util.getBucketKey()
                k.key='file_'+Util.getHash(progressID)
                k.set_contents_from_filename(path)
                k.set_acl('public-read')

                return k.key

        @staticmethod
        def transferS3FromString(title, progressID):
                k = Util.getBucketKey()
		hash_string = Util.getHash(progressID)
                k.key='title_'+ hash_string
                k.set_contents_from_string(title)
                k.set_acl('public-read')

                return k.key

        @staticmethod
        def getBucketKey():
                from boto.s3.connection import S3Connection
                conn=S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
                b = conn.get_bucket(BUCKET_NAME)
                from boto.s3.key import Key
                k = Key(b)
                return k

               


settings = {'static_path': os.path.join(os.path.dirname(__file__), "static")}
application=tornado.web.Application([
                        (r"/", MainHandler),
                        (r"/uload", UploadHandler),
                        (r"/send_text", SendText),
                        ], **settings)

if __name__ == "__main__":
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
