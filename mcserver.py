import ConfigParser, logging, datetime, os

from flask import Flask, render_template, request

import mediacloud

CONFIG_FILE = 'settings.config'
basedir = os.path.dirname(os.path.realpath(__file__))

# load the settings file
config = ConfigParser.ConfigParser()
config.read(os.path.join(basedir, 'settings.config'))

# set up logging
log_file_path = os.path.join(basedir,'logs','mcserver.log')
logging.basicConfig(filename=log_file_path,level=logging.DEBUG)
logging.info("Starting the MediaCloud example Flask app!")

# clean a mediacloud api client
mc = mediacloud.api.MediaCloud( config.get('mediacloud','api_key') )

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("search-form.html")

@app.route("/search",methods=['POST'])
def search_results():
    keywords = request.form['keywords']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    # Create datetime with datetime.datetime(year, month, day)
    start = datetime.date(int(startdate[0:4]), int(startdate[5:7]), int(startdate[8:]))
    end = datetime.date(int(enddate[0:4]), int(enddate[5:7]), int(enddate[8:]))
    results = mc.sentenceCount(keywords,
        solr_filter=[mc.publish_date_query( start, end ),
                     'tags_id_media:1' ], 
        split=True,
        split_start_date=startdate,
        split_end_date=enddate )
    splits = results['split']
    splits.pop('end', None)
    splits.pop('gap', None)
    splits.pop('start', None)
    data = [[k[0:10], v] for k, v in splits.items()]
    data.sort()
    xaxis = [str(r[0]) for r in data]
    yaxis = [r[1] for r in data]
    return render_template("search-results.html", 
        keywords=keywords, sentenceCount=results['count'], start=startdate, end=enddate, xaxis=xaxis, yaxis=yaxis )

if __name__ == "__main__":
    app.debug = True
    app.run()
