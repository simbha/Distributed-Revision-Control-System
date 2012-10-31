#! /usr/bin/python3
import exceptions,os,shutil,hashlib,datetime,filecmp,base64,difflib,sys,zlib
from optparse import OptionParser
from utils import fileTracked,getUsername,getHashNameFromHashmap


class FileController(object):
    """
    Class to perform all the local functionalities of the version
    control system.
    """
    def __init__(self):
        """
        Args:
          directory(str): Full path of the directory where the
          version control is initiated.
        Returns:
          FileController Object
        """
        self.directory = os.getcwd()
        self.statusfile = os.path.abspath(os.path.join(self.directory,'Devil','status.txt'))
        self.userfile=os.path.abspath(os.path.join(self.directory,'Devil','username.txt'))
        self.trackingfile=os.path.abspath(os.path.join(self.directory,'Devil','files.txt'))
        self.objectdir = os.path.abspath(os.path.join(self.directory,'Devil','object'))
        self.devil=os.path.abspath(os.path.join(self.directory,'Devil'))
        self.newhashmap='newhashmap.txt'

    def start(self):
        """
        Initiates the repository
        """

        try:
                os.makedirs(self.devil)
        except OSError(e):
                if e.errno != errno.EEXIST:
                    raise
        username = input("Enter username:\n")
        email = input("Enter email \n")
        uname=open(self.userfile,'w')
        uname.write(username+'\n')
        uname.write(email+'\n')
        uname.close()
        files=open(self.trackingfile,'w')
        files.close()
        files=open(self.statusfile,'w')
        files.close()

    def add(self,filename):
        """
        Adds the given file or directory (all files and directories in
        it) to the tracking system. You need to commit before the
        files added are actually tracked.

        Args:
          filename(str) : file or directory name to add
        Raises:
          FileOrDirectoryDoesNotExist : When the file or directory
          does not exist.
        """
        filename = os.path.abspath(filename)
        if(os.path.isdir(filename)):
            for i in os.listdir(filename):
                self.add(os.path.join(filename,i))
        else:
            if(fileTracked(filename,self.trackingfile)):
                print(filename + " => File added to tracking")
                files=open(self.trackingfile,'a')
                files.write(filename + " notcommited\n")
                files.close()
            else:
                print(filename + " => File already tracked")

    def commit(self,message):
        username,email = getUsername(self.userfile)
        dateandtime=str(datetime.datetime.now())
        hashmap=hashlib.sha224(base64.b64encode((username+email+dateandtime).encode('ascii'))).hexdigest()
        files=open(self.trackingfile,'r')
        lines=files.readlines();
        #os.makedirs(os.path.abspath('Devil')+'/object'+'/'+hashmap)
        for line in lines:
                #print line
                path=line.split(" ")
                if(path[1]=="notcommited\n"):
                        if(os.path.isfile(path[0])== True):
                                #print "in file ",path[0]
                                if not (os.path.exists(os.path.join(self.objectdir,hashmap))):
                                        os.makedirs(os.path.join(self.objectdir,hashmap))
                                        files=open(os.path.join(self.objectdir,hashmap,self.newhashmap),'w')
                                        files.close()
                                newhashmap=hashlib.sha224(base64.b64encode((path[0]).encode('ascii'))).hexdigest()
                                files=open(os.path.join(self.objectdir,hashmap,'newhashmap.txt'),'a')
                                files.write(path[0]+"   "+newhashmap+"\n")
                                shutil.copy2(path[0],os.path.join(self.objectdir,hashmap,newhashmap))
                        elif(os.path.isdir(path[0])== True):
                                print("in dir")
                                shutil.copytree(path[0],os.path.join(self.objectdir,hashmap))
        files=open(self.trackingfile,'w')
        for line in lines:
                path=line.split(" ")
                files.write(path[0] + " commited\n")
        files.close()
        files=open(self.statusfile,'a')
        files.write("commit "+hashmap+" "+username+" "+email+" "+dateandtime+"\n")

    def rename(self,newname):
        if os.path.exists(newname):
                raise DirectoryExist
        else:
                try:
                            os.rename(self.directory, newname)
                except OSError(e):
                            raise


    def clone(self,target):
        pass

    def log(self):
        files=open(self.statusfile)
        lines=files.readlines();
        for line in lines:
                print (line)


    def change(self,commit1,commit2):
        dir1=os.path.abspath(os.path.join(self.objectdir,commit1))
        dir2=os.path.abspath(os.path.join(self.objectdir,commit2))
        dc=filecmp.dircmp(dir1,dir2)
        dc.report_full_closure()

    def status(self):
        files=open(self.trackingfile)
        lines=files.readlines();
        for line in lines:
            line = line.split(" ")
            print("Commit: ",line[0])
            print("Author: ",line[1])
            print("Email: ",line[2])
            print("Date: ",line[3])


    def diff(self,filename):
        files=open(self.statusfile,'r')
        a=files.readlines();
        lastline=a[len(a)-1]
        files.close()
        files=open(os.path.abspath(os.path.join(self.directory,filename)),'r')
        b=files.readlines();
        files.close()
        for_commit=lastline.split("commit ")
        commit_tag=for_commit[1].split(" ")[0]
        c=self.__getFile(commit_tag,os.path.abspath(os.path.join(self.directory,filename)))
        for line in difflib.ndiff(c,b):
            print(line)


    def pull(self,url):
        pass

    def push(self,url):
        pass

    def revert(self,commit_hash):
        pass

    # Helpers
    def __objectname(self,hashtag):
        return os.path.join(self.objectdir,hashtag)



    def __getFile(self,committag,filename):
        object = os.path.join(self.objectdir,committag)
        hashmap = os.path.join(object,self.newhashmap)
        h = getHashNameFromHashmap(hashmap,filename)
        fp = zlib.open(os.path.join(object,h))
        content = fp.readlines()
        fp.close()
        return content



def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-i", "--init", help = "Initialize the repo", dest="init",action= "store_true")
    parser.add_option("-a", "--add", help = "add files to tracking system", dest="add",action= "store")
    parser.add_option("-c", "--commit",help="commit the required changes", dest="commit",action= "store")
    parser.add_option("-s", "--status",help="all not commited files", dest="status",action= "store_true")
    parser.add_option("-l", "--log",help="complete list of commits", dest="log",action= "store_true")
    parser.add_option("-d", "--diff",help="Given a file name shows diff from last commit", dest="diff",action= "store")
    parser.add_option("--change",help="overview of difference b/w two commits", dest="change",action= "store")
    (options, args) = parser.parse_args()
    if options.init:
        #print("Initializing repo")
        obj=FileController()
        obj.start()
    elif options.add:
        obj=FileController()
        #print options.add
        obj.add(options.add)
    elif options.commit:
        obj=FileController()
        obj.commit(options.commit)
    elif options.status:
        obj=FileController()
        obj.status()
    elif options.log:
        obj=FileController()
        obj.log()
    elif options.change:
        clist=options.change.split("..")
        obj=FileController()
        obj.change(clist[0],clist[1])
    elif options.diff:
        obj=FileController()
        obj.diff(options.diff)


if __name__ == "__main__":
    main()
