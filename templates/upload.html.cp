<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head> 
        <script src="/static/javascript/jquery.min.js"></script> 
        <script src="/static/javascript/jquery.form.js"></script> 
        <script src="/static/javascript/validate.js"></script> 
        <script src="/static/javascript/jquery.uploadProgress.js"></script>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/> 
        <meta name="viewport" content="width = 900"/> 
        <title>Import Delicious Bookmarks</title> 
</head>
<body>
  <!--script type="text/javascript">
        interval = null;

        function openProgressBar() {
                /* generate random progress-id */
                uuid = "";
                for (i = 0; i < 32; i++) {
                        uuid += Math.floor(Math.random() * 16).toString(16);
                }
                /* patch the form-action tag to include the progress-id */
                document.getElementById("upload").action="/upload?X-Progress-ID=" + uuid;

                /* call the progress-updater every 1000ms */
                interval = window.setInterval( function () {  fetch(uuid);  }, 1000 );
        }

        function fetch(uuid) {
        req = new XMLHttpRequest();
        req.open("GET", "/progress", 1);
        req.setRequestHeader("X-Progress-ID", uuid);
        req.onreadystatechange = function () {
                if (req.readyState == 4) {
                        if (req.status == 200) {
                                /* poor-man JSON parser */
                                var upload = eval(req.responseText);

                                document.getElementById('tp').innerHTML = upload.state;

                                /* change the width if the inner progress-bar */
                                if (upload.state == 'done' || upload.state == 'uploading') {
                                        bar = document.getElementById('progressbar');
                                        w = 400 * upload.received / upload.size;
                                        bar.style.width = w + 'px';
                                }
                                /* we are done, stop the interval */
                                if (upload.state == 'done') {
                                        window.clearTimeout(interval);
                                }
                        }
                }
        }
        req.send(null);
}
</script-->
<div style="display: block">
<form id="upload" action="/upload" method="post" enctype="multipart/form-data" target="uploadframe" onsubmit="try{return openProgressBar();}catch(e){alert(e);}">
<div><label for="title">Title</label><input type="text" name="title" id="title"></div>
<div><label for="media_file">File:<input type="file" name="media_file"></label></div>
<div><input type="submit" value="Submit"></div>
</form>
<iframe id="uploadframe" name="uploadframe" width="0" height="0" frameborder="0" border="0" src="about:blank"></iframe>
</div>
<div>
<div id="progress" style="width: 400px; border: 1px solid black">
<div id="progressbar" style="width: 1px; background-color: black; border: 1px solid white">&nbsp;</div>
</div>
</div>
<div id="response">
</div>
<div id="tp">(progress)</div>
</div>
</body>
</html>
