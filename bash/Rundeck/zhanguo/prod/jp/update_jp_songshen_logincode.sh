version=1.7.0
svndir=/svn/jp/$version/front_server/
svn up $svndir
sudo rsync  -aP  --exclude ".svn/"  --exclude "config"  $svndir    54.238.140.69::japansongshenlogin

