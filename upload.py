#!/usr/bin/python
import os, time, logging, random, urllib, shutil, memcache

import tornado.httpserver
import tornado.ioloop
import tornado.web

from hashlib import sha1
from hmac import new as hmac

from httplib import HTTP
from urlparse import urlparse

AWS_ACCESS_KEY='AKIAJ5TKKYN3Q7BPXCBQ'
AWS_SECRET_KEY='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'
BUCKET_NAME='soundcloudr'
BUCKET_URI='https://s3-eu-west-1.amazonaws.com/soundcloudr/'
#TMP_FILE_STORAGE='/home/ec2-user/sounduploadr/tmp/'
FILE_UPLOAD_STORAGE='/var/www/sounduploadr/file/'
FILE_UPLOAD_URI='/file/'


mc = memcache.Client(['127.0.0.1:11211'], debug = 1)

class MainHandler(tornado.web.RequestHandler):
        def get(self):
                self.set_header('Content-Type', 'text/html')
                #self.render("templates/upload.html.cp.1", title="Uplaod test" , data= [])
                self.render("index.html", title="Upload test" , data= [])
class SendText(tornado.web.RequestHandler):
        def get(self):
                title = tornado.escape.utf8(self.get_argument('title', ''))
                #title = unicode(self.get_argument('title', ''))
                progressID = self.get_argument('X-Progress-ID', None)

		s3File = None
		check_pID = mc.get(str(progressID))

		if progressID is None or not check_pID:
			logging.info('Progress Id is missing or invalid')
			self.write('Request can\'t be proceesed without proper progressID')
			return
		hashProgressID = Util.getHash(progressID)

		if len(title) > 0:
                	s3File = Util.transferS3FromString(title, progressID)
			titleUrl = BUCKET_URI + 'title_'+ hashProgressID
			self.write("Title '%s' backup location:" % title)
                        self.write("<a href=\"%s\">%s</a><br>" %(titleUrl,titleUrl))
                else:
                        self.write('Title: no data<br>')

                fileUrl = FILE_UPLOAD_URI + 'file_'+ hashProgressID
                backupFileUrl = BUCKET_URI + 'file_'+ hashProgressID

                self.write("File location:")
                self.write("<a href=\"%s\">%s</a><br>" %(fileUrl ,fileUrl))
                self.write("backup location (soon available):")
                self.write("<a href=\"%s\">%s</a><br>" %(backupFileUrl ,backupFileUrl))

class UploadHandler(tornado.web.RequestHandler):
        def post(self):
                title = self.get_argument('title', default=None)
                self.set_header('Content-Type', 'text/html')
                progressID = self.get_argument('X-Progress-ID' , default=None)
                filename = self.get_argument('media_file.name', default=None)
                path = self.get_argument('media_file.path', default=None)
                size = self.get_argument('media_file.size', default=None)

		if path is None:
			logging.info('No file uploaded')
			return

		if progressID is None:
			logging.info('Progress Id is missing')
			self.write('Request can\'t be proceesed without progressID')
			return
		hashProgressID = Util.getHash(progressID)
		mc.set(str(progressID), '1')
		src=path
		dst='%sfile_%s' %(FILE_UPLOAD_STORAGE, hashProgressID)
		shutil.move(src,dst)

                #fileNameS3=u.transferS3FromFile(path, TMP_FILE_STORAGE, progressID)
                #fileNameS3=Util.transferS3FromFile(path, progressID)
                #fileUrl = BUCKET_URI+fileNameS3

                self.write('message:%s<br>filename %s<br>path:%s<br>progressID:%s<br>size %s<br>' % (title, filename, path, progressID, size))
                
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
	@staticmethod
	def checkUrl(url):
		p = urlparse(url)
		h = HTTP(p[1])
		h.putrequest('HEAD', p[2])
		h.endheaders()
		if h.getreply()[0] != 404:
			return True
		return False

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
