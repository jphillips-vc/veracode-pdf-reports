import os, sys
import json
import xmltodict
import datetime
import argparse
from datetime import date
from datetime import timedelta
#
# GLOBAL VARIABLES
# 
JavaWrapperVersion="20.8.7.1"
now = datetime.datetime.now()
today = date.today()  
yesterday = today - timedelta(days = 1) 
reportfrom = str(yesterday.month)+'/'+str(yesterday.day)+'/'+str(yesterday.year)
builds_dict={}
#
# CLI Parser //  --summary flag will create summary pdf reports
#
parser = argparse.ArgumentParser(description='Accept flags from CLI')
parser.add_argument('--summary', dest='report', action='store_true', help="--summary creates a summary pdf report [default]")
parser.add_argument('--detailed', dest='report', action='store_false', help="--detailed option creates detailed pdf report")
parser.set_defaults(report=True)
args = parser.parse_args()
reporttype = args.report
#
# IMPORT XML AND CAPTURE DATA
#
def getData():
	#
	# CAPTURE XML DATA FROM VERACODE (assumes you have credentials file in place)
	#
	# DOWNLOAD API WRAPPER
	os.system('curl -sSo VeracodeJavaAPI.jar https://repo1.maven.org/maven2/com/veracode/vosp/api/wrappers/vosp-api-wrappers-java/'+str(JavaWrapperVersion)+'/vosp-api-wrappers-java-'+str(JavaWrapperVersion)+'.jar')
	#
	# GET DATA
	os.system('java -jar VeracodeJavaAPI.jar -action getappbuilds -reportchangedsince '+str(reportfrom)+' > recent_veracode_builds.xml')
	#os.system('java -jar VeracodeJavaAPI.jar -action getappbuilds -reportchangedsince 01/01/2020 > recent_veracode_builds.xml')
	#
	# CREATE REPORT DIRECTORY
	os.system('mkdir veracode_pdf_reports')	
	#
	# Importing XML data and convert to JSON
	#
	try:
		with open('recent_veracode_builds.xml') as xml_file:
			data_dict = xmltodict.parse(xml_file.read())
			xml_file.close()
		json_data = json.dumps(data_dict, indent=4)
	except:
		cleanup()
		print(sys.exc_info())
		sys.exit("Error importing XML [see getData()]")
	#
	# WRITE TO JSON FILE
	#
	try:
		f = open("recent_veracode_builds.json", "w")
		f.write(json_data.replace('@', 'vc_'))
		f.close()
	except:
		cleanup()
		print(sys.exc_info())
		sys.exit("Error writing JSON [see getData()]")
	#
	# IMPORT JSON FILE AS OBJECT
	#
	try:
		with open('recent_veracode_builds.json') as json_file:
			build_json = json.load(json_file)
			builds = build_json['applicationbuilds']
			json_file.close()
	except:
		cleanup()
		print(sys.exc_info())
		sys.exit("Error reading JSON [see getData()]")
	#
	# CREATE DATASET
	#
	try:
		buildcount=0
		for i in builds['application']:
			if "build" in i: 
				app_id = i['vc_app_id']
				app_name = i['vc_app_name']
				build_id = i['build']['vc_build_id']
				analysis_type = i['build']["analysis_unit"]["vc_analysis_type"]
				published_date = i['build']["analysis_unit"]["vc_published_date"]
				builds_dict[buildcount]={'app_id' : app_id, 'app_name' : app_name, 'build_id' : build_id, 'analysis_type' : analysis_type, 'published_date' : published_date}
			buildcount=buildcount+1
	except: 
		print(sys.exc_info())
		cleanup()
		sys.exit("Error creating builds_dict [see getData()]")
#
# CREATE REPORTS
#
def createReports():
	getData()
	try:
		for k, v in builds_dict.items():
			bid = str(builds_dict[k]['build_id'])
			if reporttype is True:
				file_name = str(builds_dict[k]['app_name'].lower().replace('.', '-').replace('_', '-').replace(' ', '').replace('.html', '').replace('http://', '').replace('https://', '').replace('/', ''))+'_'+str(builds_dict[k]['analysis_type'].lower())+'_Report.pdf'
				print(bid, file_name)
				os.system('java -jar VeracodeJavaAPI.jar -action summaryreport -buildid '+ str(bid) +' -format pdf -outputfilepath veracode_pdf_reports/'+ str(file_name))
			else:
				file_name = str(builds_dict[k]['app_name'].lower().replace('.', '-').replace('_', '-').replace(' ', '').replace('.html', '').replace('http://', '').replace('https://', '').replace('/', ''))+'_'+str(builds_dict[k]['analysis_type'].lower())+'_DetailedReport.pdf'
				print(bid, file_name)
				os.system('java -jar VeracodeJavaAPI.jar -action detailedreport -buildid '+ str(bid) +' -format pdf -outputfilepath veracode_pdf_reports/'+ str(file_name))	
		cleanup()
	except:
		print(sys.exc_info())
		cleanup()
		sys.exit("Error creating reports.  [see createReports()]")
#
# CLEAN UP
#
def cleanup():
	try:
		os.system('rm VeracodeJavaAPI.jar')
		os.system('rm recent_veracode_builds.xml')
		os.system('rm recent_veracode_builds.json')
	except:
		sys.exit("Error cleaning up temp files")

def main():
	#
	# Rock 'n Roll
	#
	createReports()
	
main()