from flask import Flask, render_template
import urllib.request
import os
import boto3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/meta')
def meta():
    url = "http://169.254.169.254/latest/meta-data/"

    metadata_list = urllib.request.urlopen(url).read().decode()
    str = "Metadata\n"

    for k in metadata_list.split('\n'):
        url_with_key = url + k
        v = urllib.request.urlopen(url_with_key).read().decode()
        str = str + "<tr><td>%s</td><td>%s</td></tr>" % (k, v)

    html = "<html><body><table>%s</table></body></html>" % str

    return html

@app.route('/load')
def load():
    idleCpu = int(os.popen('vmstat 1 2 | awk \'{ for (i=1; i<=NF; i++) if ($i=="id") { getline; getline; print $i }}\'').read())
    
    if idleCpu > 50:
        os.system('dd if=/dev/zero bs=100M count=500 | gzip | gzip -d  > /dev/null &')
        return '<p>Current CPU load is %s</p><p>Generating CPU Load!</p>' % str(100 - idleCpu)
    else:
        return '<p>Current CPU load is %s</p><p>Under High CPU Load!</p>' % str(100 - idleCpu)

@app.route('/s3/<bucket_name>')
def list_s3(bucket_name):
    s3  = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    file_list = ""
    for file in bucket.objects.all():
        file_list = file_list + "<li>%s</li>" % file.key
    
    html = "<html><body><ol>%s</ol></body></html>" % file_list
    return html

if __name__ == '__main__':
    app.run()
