node {
   stage('Get Source') {
      // copy source code from local file system and test
      // for a Dockerfile to build the Docker image
      git ('https://github.com/Tylerlhess/squawker-web.git')
      if (!fileExists("Dockerfile")) {
         error('Dockerfile missing.')
      }
   }
   stage('Build/Run Docker') {
       // build the docker image from the source code using the BUILD_ID parameter in image name
       def img = docker.build("squawker_web:${env.BUILD_ID}")
       img.withRun("-p 8010:8000")

    }
}
