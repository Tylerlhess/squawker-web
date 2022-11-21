node {
    try {
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
            img.withRun("-p 8010:8000") {
                sh 'pytest'
                sh "sleep 1"
            }

        }
    } finally {
        // Clean after build
        cleanWs(cleanWhenNotBuilt: false,
            deleteDirs: true,
            disableDeferredWipeout: true,
            notFailBuild: true,
            patterns: [[pattern: '.gitignore', type: 'INCLUDE'],
                       [pattern: '.propsfile', type: 'EXCLUDE']])
    }
}