node {
   stage('Get Source') {
      // copy source code from local file system and test
      // for a Dockerfile to build the Docker image
      git ('https://github.com/Tylerlhess/squawker-web.git')
      if (!fileExists("Dockerfile")) {
         error('Dockerfile missing.')
      }
   }
   stage('Build Docker') {
       // build the docker image from the source code using the BUILD_ID parameter in image name
         sh "sudo docker build -t squawker-web ."
   }
   stage("run docker container"){
        sh "sudo docker run -p 8010:8000 --name squawker-web -d squawker-web "
    }
}
