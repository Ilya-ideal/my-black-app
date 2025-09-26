pipeline {
    agent any

    environment {
        // Эти переменные будут заданы в настройках Jenkins
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        TELEGRAM_BOT_TOKEN = credentials('telegram-bot-token')
        TELEGRAM_CHAT_ID = credentials('telegram-chat-id')
        DOCKER_IMAGE = 'your-dockerhub-username/my-black-app'
        KUBE_CONFIG = credentials('kubeconfig') // Конфиг для доступа к Kubernetes
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm // Получаем код из GitHub
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Логинимся в Docker Hub
                    sh "echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin"
                    
                    // Собираем образ
                    sh "docker build -t ${DOCKER_IMAGE}:latest ."
                    
                    // Пушим образ
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // Сохраняем kubeconfig для kubectl
                    writeFile file: 'kubeconfig.yaml', text: "${KUBE_CONFIG}"
                    
                    // Обновляем образ в deployment
                    sh "kubectl --kubeconfig=kubeconfig.yaml set image deployment/my-black-app app=${DOCKER_IMAGE}:latest"
                    
                    // Ждем пока деплоймент обновится
                    sh "kubectl --kubeconfig=kubeconfig.yaml rollout status deployment/my-black-app --timeout=300s"
                }
            }
        }

        stage('Send Telegram Notification') {
            steps {
                script {
                    // Отправляем уведомление в Telegram
                    def message = "✅ Деплой успешно завершен!\\nПриложение с черным фоном запущено.\\nВремя: ${new Date()}"
                    sh """
                        curl -s -X POST \
                        https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage \
                        -d chat_id=${TELEGRAM_CHAT_ID} \
                        -d text="${message}"
                    """
                }
            }
        }
    }

    post {
        failure {
            script {
                // Уведомление об ошибке
                def message = "❌ Деплой провалился!\\nПроверьте Jenkins: ${env.BUILD_URL}"
                sh """
                    curl -s -X POST \
                    https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage \
                    -d chat_id=${TELEGRAM_CHAT_ID} \
                    -d text="${message}"
                """
            }
        }
    }
}