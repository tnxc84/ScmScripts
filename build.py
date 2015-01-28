#!/usr/bin/env python
#**********************************************************************************/
# FILENAME:     build.py
# Copyright(c) 2004 Symbol Technologies Inc.  All rights reserved.
#
# DESCRIPTION:  Generic script 'build.py' is used for all builds. The actural build 
#               is performed by the build scripts specified in the <buildscript> tags.                
# NOTES:         
#
# AUTHOR:      Ke Zhang 
#                
# CREATION DATE: 11/19/2004
# DERIVED FROM:  build_tnt.py
#
# EDIT HISTORY:
#   $Log: build.py,v $
#   Revision 1.29  2007/07/26 18:29:36  spinagent
#   07/26/07:   1.  Making modification to allow insert of xml logs into spin.xml
#
#   Revision 1.28  2007/07/26 17:51:48  spinagent
#   test
#
#   Revision 1.27  2005/06/06 12:56:43  spinagent
#      06/06/05:
#                  1.  Current build result compress file name are
#                              "<buildname>_release.zip" or ".tz' file
#                              "<buildname>_eng.zip" or ".zip" file
#                      Now, the filename will be change with "<porjectname>_" before upload,
#                      filename looks like:
#                          "<porjectname>_<buildname>_release.zip" or ".tz' file
#                          "<porjectname>_<buildname>_eng.zip" or ".zip" file
#                  2.  Current build result compress file name is
#                          "<buildname>_log.zip" or ".tz' file
#                      Change to "<porjectname>_<buildname>_log.zip" or ".tz' file
#                      before upload to local FTP server.
#
#   Revision 1.26  2005/05/31 16:54:46  spinagent
#      05/31/05:
#                  1.  When upload Agent Script log failed, it is UNFAIR to set build status
#                      to 'failed', fix this bug.
#
#   Revision 1.25  2005/05/11 22:02:46  spinagent
#      05/11/05:
#                  1.  When compress log files, it needs not to compress 'link' file. So,
#                      modify function 'Compress()' to filter out 'link' file. Otherwise,
#                      it will render exception too.
#
#   Revision 1.24  2005/04/13 20:02:21  spinagent
#      04/13/05:
#                  1.  Build script default parameter change from 'buildnumber' to 'buildname'
#                      as  'buildnumber' => 'buildname'
#
#   Revision 1.23  2005/03/23 18:32:41  spinagent
#      03/23/05:
#                  1.  Report parsing error in XML format log files into 'agent_script.log'
#                      and remove it before inserting it into the 'spin.xml'
#
#   Revision 1.22  2005/02/22 13:36:55  spinagent
#      02/22/05:
#                  1.  When Upload agent script log file error, set <buildstatus> to 'Failes' and
#                      <builderror> to 'Upload Agent script File Failed'.
#
#   Revision 1.21  2005/02/18 22:05:15  spinagent
#      02/18/05:
#                  1.  When Upload build files error, set <buildstatus> to 'Failes' and
#                      <builderror> to 'Upload Build Files Failed'.
#
#   Revision 1.20  2005/02/18 21:41:33  spinagent
#      02/18/2005: V1.0.1
#                  1. Add 'pass' in exception section of upload build files.
#
#   Revision 1.19  2005/02/08 18:26:45  spinagent
#      02/08/05:
#                  1.  Start build script by combine Python interpretor, when buildscript
#                      is written in Python, this is accomadate Windows'98 system. Because,
#                      98 can not associate Python interpretor in DOS window. 'start' command
#                      in 98 can only start a new program.  Win98 is only for testing,
#                      modification here makes this generic.  If the script is in Perl, or
#                      what else on Win98 platform, they may added later.
#
#   Revision 1.18  2005/01/31 15:56:51  spinagent
#      01/28/05:
#                  1.  Check 'cancel.lock' file, if it exists, then remove it and get out
#                      of loop. No more build scripts will be executed.
#                      It is used to implement 'soft' cancel.
#                  2.  'agent_script.log' file will be uploaded to the FTP repository
#                      after each build script is executed.
#
#   Revision 1.17  2005/01/18 21:07:17  spinagent
#   Directories 'logs&build' will NOT be cleaned at the end of build.py
#   They will be cleaned before new job is initiated. The clean is implemented in
#   'Sccs_Get' module.
#
#   Revision 1.16  2005/01/18 15:33:27  spinagent
#   New Version Build.py:
#
#   1. Split build scripts runing squence.  Log files will be parsed and upload to local  FTP
#   repository after each build script is finished.  Thus, users could access each step
#   build information.
#
#   2. If build scripts generate XML format log files by themselves. Build.py would NOT parse
#   the free style log files any more, just insert these XML files into the 'SPIN.XML' file.
#
#   3. <status> in these XML files would be read to determince the build status.
#
#   Revision 1.15  2005/01/14 15:45:40  spinagent
#   Replace all 'print' => 'logprint'
#
#   Revision 1.14  2005/01/14 15:36:27  spinagent
#   Add log history for Edit
#
#   11/19/04:
#               1.  Define the algorithm for 'Build.py'.
#                   1). Parse 'spin.xml' file to extract buildscript list to be 
#                       executed.
#                   2). Create directories './logs', './build/release' and 
#                       './build/engineering'.
#                   3). Loop for 'buildscript' in 'buildscript list'
#                       3.1). execute buildscript 
#                       3.2). other processing 
#                   4). Create XML format log files from free style log files
#                   5). Insert log XML file content into 'spin.xml' file according  
#                       to the creation time, then remove all XML log files.
#                   6). Zip all free style log files into an "BuildName_log.zip",
#                       then remove all free style log files.
#                   7). Upload all build and log files (release and engineering  
#                       files) to the local ftp repository.
#                   8). Clean up .Zip files under 'build' and 'logs' directories.
#                   9). The 'status' is set to 'Complete'
#   11/22/04:
#               1.  Create function 'Compress()' to '.zip' archive files for log
#                   files under subdirectory './logs'.  The archive file name 
#                   is 'buildname_log.zip'.  Currently, consider to create '.zip'
#                   file on "Windows" platform. Consider to create '.tz' archive
#                   on "Linux" platform.
#   12/01/04:
#               1.  Change FTP repository to new format.
#                   ftp://<spin server name>/<product family>/
#                       <project name>_<project_version string>/<buildtype>/
#                       <buildname>/
#                   and the subdirectories are 'logs', 'release' and 'engineering'
#   01/14/05:
#               1.  Replace all 'print' => 'logprint', to suppress output to screen. 
#                   Hope this will eliminate 'stuck' issue. 
#   01/17/05:
#               1.  Split build script processing steps.  After each build script
#                   finished, log files will be upload to the FTP repository, it's
#                   corresponding XML format log files will be inserted into  the 
#                   'spin.xml' file. Thus, users will see the building 'delta' results 
#                   dynanically.
#               2.  XML log file <status> is read to determine the build status, 
#                   if at least one <status> is not 'Pass', thus the whole build
#                   status will be set to 'Failed'
#   01/28/05:
#               1.  Check 'cancel.lock' file, if it exists, then remove it and get out
#                   of loop. No more build scripts will be executed. 
#                   It is used to implement 'soft' cancel. 
#               2.  'agent_script.log' file will be uploaded to the FTP repository
#                   after each build script is executed. 
#   02/08/05:
#               1.  Start build script by combine Python interpretor, when buildscript
#                   is written in Python, this is accomadate Windows'98 system. Because,
#                   98 can not associate Python interpretor in DOS window. 'start' command 
#                   in 98 can only start a new program.  Win98 is only for testing, 
#                   modification here makes this generic.  If the script is in Perl, or 
#                   what else on Win98 platform, they may added later.
#   02/18/05:
#               1.  When Upload build files error, set <buildstatus> to 'Failes' and 
#                   <builderror> to 'Upload Build Files Failed'. 
#   03/23/05:
#               1.  Report parsing error in XML format log files into 'agent_script.log' 
#                   and remove it before inserting it into the 'spin.xml'
#   04/13/05:
#               1.  Build script default parameter change from 'buildnumber' to 'buildname'
#                   as  'buildnumber' => 'buildname'
#   05/11/05:
#               1.  When compress log files, it needs not to compress 'link' file. So,
#                   modify function 'Compress()' to filter out 'link' file. Otherwise,
#                   it will render exception too.
#   05/31/05:
#               1.  When upload Agent Script log failed, it is UNFAIR to set build status
#                   to 'failed', fix this bug. 
#   06/06/05:
#               1.  Current build result compress file name are
#                           "<buildname>_release.zip" or ".tz' file
#                           "<buildname>_eng.zip" or ".zip" file
#                   Now, the filename will be change with "<porjectname>_" before upload,
#                   filename looks like:
#                       "<porjectname>_<buildname>_release.zip" or ".tz' file
#                       "<porjectname>_<buildname>_eng.zip" or ".zip" file
#               2.  Current build result compress file name is
#                       "<buildname>_log.zip" or ".tz' file
#                   Change to "<porjectname>_<buildname>_log.zip" or ".tz' file
#                   before upload to local FTP server.
#
#   07/26/07:   1.  Making modification to allow insert of xml logs into spin.xml
#                   
#**************************************************************************************/

import os
import sys
import glob
import string
import spinutil
import Parse_XML
import zipfile
import shutil
import re
pytp = re.compile('.*\.py.*', re.IGNORECASE)

from xml.dom.ext.reader.Sax2 import FromXmlStream
from xml.xpath import Evaluate
from string import strip

spinxmlname = 'spin.xml'

global spinlogfile

# In order to write the log file to a specific position
# Append the absolute path before the logfile name.
abspath = os.path.abspath(os.path.dirname(__file__))
spinlogfile = 'spin.log'
spinlogfile = os.path.join(abspath, spinlogfile)

agentlog = 'agent_script.log'
#agentlog = os.path.join(abspath, agentlog)

cancellockfile = 'cancel.lock'
cancellockfile = os.path.join(abspath, cancellockfile)

##########################################################################################
##  Compress(zipf,f) --- insert 'f' into archive 'zipf'                                 ##
##########################################################################################
def Compress(zipf, f):
    status = 0
    try:        
        if os.path.exists(zipf):
            spinutil.logprint("Append '%s' to Zip file: '%s'" % (f, zipf))
            file = zipfile.ZipFile(zipf, "a")
        else:
            spinutil.logprint("Append '%s' to new created Zip file: '%s'" % (f, zipf))
            file = zipfile.ZipFile(zipf, "w")
        if os.path.isfile(f):
            file.write(f, os.path.basename(f), zipfile.ZIP_DEFLATED)
        file.close()
    except:
        status = "Error --- write File:'%s' => Zip File:'%s'." % (f, zipf)
        spinutil.logprint(status)
        raise    
    return status

##########################################################################################
##  ChangeBuildName(projectname) --- Modify build result filename to combine            ##
##                                  'projectname' if it not.                            ##
##########################################################################################
def ChangeBuildName(projectname):
    status = 0

    restr = '.*%s.*' % projectname
    pjpattern = re.compile(restr, re.IGNORECASE)
    
    try:     
        rlfdir = os.path.join(abspath, 'build', 'release')
        rlflist = os.listdir(rlfdir)
        for rlf in rlflist:
            if pjpattern.findall(rlf) == []:
                srcfile = os.path.join(rlfdir, rlf)
                dstfilename = projectname + '_' + rlf
                dstfile = os.path.join(rlfdir, dstfilename)
                shutil.move(srcfile, dstfile)    # Rename file
    except:
        status = "Error --- Changing Build Release File Name with projectname: %s" % (projectname)
        spinutil.logprint(status)
        raise
    
    try:
        engdir = os.path.join(abspath, 'build', 'engineering')
        engflist = os.listdir(engdir)
        for eng in engflist:
            if pjpattern.findall(eng) == []:
                srcfile = os.path.join(engdir, eng)
                dstfilename = projectname + '_' + eng
                dstfile = os.path.join(engdir, dstfilename)
                shutil.move(srcfile, dstfile)    # Rename file
    except:
        status = "Error --- Changing Build Engineering File Name with projectname: %s" % (projectname)
        spinutil.logprint(status)
        raise    

    return status

##########################################################################################
##  main() --- main function of 'build.py'                                              ##
##########################################################################################
def main():
    global spinlogfile
    buildstatus = 'Pass'
    builderror = 'Build success'
    try:
        # Parse Job description XML file to get buildscript list
        try:
            agent_scripts = {}
            Parse_XML.GetAgentScriptInfo(spinxmlname, agent_scripts)
            #debugprint ( status)            
        except:
            status = "Error --- parsing Job Description file. "
            #debugprint ( status )
            pass

        # Create directories to store log and build output information.
        # Directories: 'logs', 'build\release' and 'build\engineering'

        dir = os.getcwd()
        try:
            if spinutil.mswindows:
                if not os.path.isdir('logs'):
                    os.mkdir("logs")
                if not os.path.isdir('build'):
                    os.mkdir("build")
                    os.mkdir(".\\build\\release")
                    os.mkdir('.\\build\\engineering')
                if not os.path.isdir('.\\build\\release'):
                    os.mkdir(".\\build\\release")
                if not os.path.isdir('.\\build\\engineering'):
                    os.mkdir('.\\build\\engineering')
            else:
                if not os.path.isdir('logs'):
                    os.mkdir("logs")
                if not os.path.isdir('build'):
                    os.makedirs("build/release")
                    os.makedirs("build/engineering")
                if not os.path.isdir('build/release'):
                    os.makedirs("build/release")
                if not os.path.isdir('build/engineering'):
                    os.makedirs("build/engineering")
                spinutil.run('chmod -R 755 ./* ')
        except:
            spinutil.logprint("Error --- Create 'agentroot/build' and/or 'agentroot/logs' directories.")
            pass

        # Generate compressed log file name and clean that file, if it exists in advance.
        projectname = string.strip(agent_scripts['projectname'])
        zipf = projectname + '_' + string.strip(agent_scripts['buildname']) + '_logs.zip'
        zipf = os.path.join('logs', zipf)
        if os.path.exists(zipf):
            os.remove(zipf)

        # Start Builing ... ...
        spinutil.setstatus('Building')
        buildscriptlist = agent_scripts['scriptlist']['buildscript']
        # Variables to preserve log file list. 
        #pre_filelist = []
        filelist = []
        for buildscript in buildscriptlist:
            
            # Check 'cancel.lock' file, it exists, then break out of the loop for 'soft' cancel.
            if os.path.isfile(cancellockfile):
                os.remove(cancellockfile)
                spinutil.logprint ('Build job cancelled')                
                break

            spinutil.setstatus(buildscript['displaystatus']) # Setup <status> based on <displaystatus>
##            buildcommand = '%s %s %s'% (buildscript['name'], agent_scripts['buildnumber'], buildscript['arguments'])
            buildcommand = '%s %s %s'% (buildscript['name'], agent_scripts['buildname'], buildscript['arguments'])
            if pytp.findall(buildscript['name']) <> [] and spinutil.mswindows:
                buildcommand = os.path.join(sys.prefix, 'python.exe ') + buildcommand
            #print "Run buildscript %s ..." % buildcommand
            spinutil.logprint("Run buildscript %s ..." % buildcommand)
            spinutil.run(buildcommand)
            # Tracking log file generating sequence for log files insertion into 'spin.xml' later
            # Othe processing

            # After each buildscript is executed, log files are to be processed.
            os.chdir(dir)

            # Logg files may have other extension name. It need to change into the 'logs'
            # directory for following processing. 
            filelist = os.listdir('logs')

            # Remove '.zip' file names from the file list.
            path = os.path.join('logs', '*.zip')
            zipfilelist = glob.glob(path)
            if zipfilelist <> []:
                for f in zipfilelist:
                    ff = os.path.basename(f)
                    if ff in filelist:
                        filelist.remove(ff)
            
            # 'Substrct' 'pre_filelist' from the current 'filelist'.
            #    for f in pre_filelist:
            #        if f in filelist:
            #            filelist.remove(f)
            # Update 'pre_filelist' to the current filelist.
            #pre_filelist = pre_filelist.extend(filelist)
            
            path = os.path.join('logs', '*.xml')
            xmlfilelist = glob.glob(path)
            
            fdict = {}
            #print filelist
            if xmlfilelist == []:
                # Branch Successful ---
                # No XML format generated by build script, free style log files are to be parsed to generate
                # XML format log files, then to insert in to 'spin.xml' file.
                os.chdir('logs') # If using 'glob' module, this will be moved in front of the next loop.
                for f in filelist:
                    list = []    
                    try:
                        ctime = os.path.getctime(f)
                        #print ctime
                        if ctime in fdict.keys():
                            fdict[ctime].append(os.path.basename(f))
                        else:
                            list.append(os.path.basename(f))
                            fdict[ctime] = list
                    except:
                        spinutil.logprint("Error --- get file creation time")
                        pass
            
                ctimelist = fdict.keys()
                ctimelist.sort()
    
                #os.chdir('logs')
                logxmlfilelist = []
                for ctime in ctimelist:
                    for logfile in fdict[ctime]:
                        #print f
                        (lname,lext) = os.path.splitext(logfile)
                        logxmlfile = lname + "_log.xml"
                        # Generate log XML file from each free style log file.
                        logtype = None
                        if string.lower(agent_scripts['projectname']) == 'ws5000':
                            logtype = 'ws5000build'
                        elif string.lower(agent_scripts['projectname']) == 'tntfusion':
                            logtype = 'tntfusionbuild'
                    
                        if logfile == 'agent_script.log':
                            st = spinutil.makexmllog(logxmlfile, 'agentscriptlog', logfile, logtype)
                        else:
                            st = spinutil.makexmlfile(logxmlfile, 'buildlog', logfile, logtype)
                        if st == 2:
                            buildstatus = 'Failed'
                            builderror = 'Build failed'
                        # Track xmlfile name into the list.
                        logxmlfilelist.append(logxmlfile)
            else:
                # Branch Fail ---
                # XML format generated by build script, free style log files need NOT to be parsed to 
                # generateXML format log files;  Those XML log files could be inserted in to 'spin.xml' file directly.
                # Those xml logfile name need to be removed from 'pre_filelist'

                # Remove the XML file list from 'filelist'
                for f in xmlfilelist:
                    #if f in pre_filelist:
                    #    pre_filelist.remove(f)
                    ff = os.path.basename(f)
                    if ff in filelist:
                        filelist.remove(ff)
                        
                for f in xmlfilelist:
                    list = []    
                    try:
                        ctime = os.path.getctime(f)
                        #print ctime
                        if ctime in fdict.keys():
                            fdict[ctime].append(os.path.basename(f))
                        else:
                            list.append(os.path.basename(f))
                            fdict[ctime] = list
                    except:
                        spinutil.logprint("Error --- get file creation time")
                        pass
            
                ctimelist = fdict.keys()
                ctimelist.sort()
    
                logxmlfilelist = []
                for ctime in ctimelist:
                    for logfile in fdict[ctime]:
                        # Track xmlfile name into the list.
##                        logxmlfilelist.append(logfile)
                        
                        # open the xml file and parse in to a DOM tree so we can use the XPath functions
                        try:
                            lf = os.path.join('logs', logfile)
                            fp = open(lf,'r')
                            dom = FromXmlStream(fp)
                            fp.close()
                            
                           # Check 'status', if it is NOT 'Pass', then 'buildstatus' is set to 'Failed'
                            status = strip(Evaluate('/buildlog/status/text()', dom.documentElement)[0].nodeValue)
                            if string.lower(status) <> 'pass':
                                buildstatus = 'Failed'
                                builderror = 'Build Failed' # Or a tag's content in the XML file.              
                            # Track xmlfile name into the list, when it's format is succssfully parsed.
                            logxmlfilelist.append(logfile)
                        except:
                            spinutil.logprint( "Error in format of XML log file: '%s'" % lf)
                            os.remove(lf) # Remove this error format XML file
                            pass
                            #raise
 
            os.chdir(dir)         
            # Insert each XML format log file content into 'spin.xml'
            # and remove each '.xml' log file after it is inserted.
            for logxmlfile in logxmlfilelist:
                lxf = logxmlfile
                # Add this specific log xml file into 'spin.xml'
                if sys.platform == "win32":
                    logxmlfile = os.path.join('logs', logxmlfile)   #changed this -DM 7/26
                    #logxmlfile = 'logs\\\\\\%s' % logxmlfile
                    #print logxmlfile
                else:
                    logxmlfile = os.path.join('logs', logxmlfile)
                    #logxmlfile = 'logs//////%s' % logxmlfile
            
                if lxf == 'agent_script_log.xml':
                    spinutil.addlog(logxmlfile, 'agentscriptloglist')
                else:
                    spinutil.addlog(logxmlfile, 'buildloglist')
                
                #spinutil.logprint_local ("Insert log XML file  %s ..." % logxmlfile, spinlogfile)
                # Remove the XML format log file after its content is inserted into the 'spin.xml' file.
                os.remove(logxmlfile)
    
            # Zip all free style log files, Then, PutBuildfiles() will responsible to upload
            # all build '.zip' and log '.zip' files to the local FTP repository.
            os.chdir(dir)
            for logfile in filelist:
                logfile = os.path.join('logs', logfile)
                #print logfile
                Compress(zipf,logfile)
                os.remove(logfile)
                
            # Copyt 'agent_script.log' into 'logs' directory, thus, intermedia agent_script.log could be seen
            #if os.path.isfile('agent_script.log'):
            #    srcfile = 'agent_script.log'
            #    dstfile = os.path.join('logs', 'agent_script.log')
                # Copy agent script log file into 'logs' directory
            #    shutil.copy(srcfile, dstfile) 
                
            # upload the build to ftp server
            spinutil.setstatus('Uploading Build and Log files')
            ChangeBuildName(projectname)
            try:
                projectname_version = string.strip(agent_scripts['projectname'])+ '_' + string.strip(agent_scripts['projectversion'])
                buildtypestr = string.strip(agent_scripts['buildtype'])
                if  buildtypestr == 'X' or buildtypestr == 'x':
                    buildtype = 'engineering'
                else:
                    buildtype = 'official'
                
                destinationpath = "/%s/%s/%s/%s" %(string.strip(agent_scripts['productfamily']),
                        projectname_version,
                        buildtype,
                        string.strip(agent_scripts['buildname']))
                spinutil.logprint(destinationpath)
                st = spinutil.putbuildfiles(destinationpath)
                if st == 2:
                    buildstatus = 'Failed'
                    builderror = 'Build failed'
            except:
                buildstatus = 'Failed'
                builderror = 'Upload Build Files Failed'
                spinutil.logprint(builderror)
		pass

            # Remove 'agent_script.log' from 'logs' directory, otherwise, this log file would be compressed into log ZIP file.
            #dstfile = os.path.join('logs', 'agent_script.log')
            #if os.path.isfile(dstfile):
                # Remove agent script log file into 'logs' directory
            #    os.remove(dstfile)
            
            # Upload 'agent_script.log' to FTP repository, thus, intermedia 'agent_script.log' could be seen
            destagentlog = '%s/logs/%s' % (destinationpath, agentlog)
            if os.path.isfile(agentlog):
                try:
                    spinutil.putbuild(agentlog, destagentlog)
                except:
                    #buildstatus = 'Failed'
                    uperror = 'Upload Agent Script Log File Failed'
                    spinutil.logprint(uperror)
                    pass                           
        # clean up
        spinutil.setstatus('Cleaning up')
        spinutil.setbuildstatus(buildstatus, builderror)
 
        # These command would clean all files and directories under the directory
        # The clean function is commented out. 01/18/05.  These dirs will be cleaned before 
	# new job is initiated.
        #if spinutil.mswindows:
        #    spinutil.run('rmdir /q /s logs')
        #    spinutil.run('rmdir /q /s build')
        #else:
        #    spinutil.run('rm -rf logs')
        #    spinutil.run('rm -rf build')
            
        #spinutil.setstatus('Complete')  # This stautus will be set in Agent('runscript.py')
    except:
        status = "Error --- Execute Agent Build Script ('build.py'). "
        spinutil.logprint(status)
        raise

if __name__ == "__main__":
    main()
