node {
  def acr = 'acrdemo66.azurecr.io'
  def appName = 'dockerimage'
  def imageName = "${acr}/${appName}"
  def imageTag = "${imageName}:${env.BRANCH_NAME}.${env.BUILD_NUMBER}"
  def appRepo = "acrdemo66.azurecr.io/dockerimage:v1.0"

  checkout scm
  
 stage('Build the Image and Push to Azure Container Registry') 
 {
   app = docker.build("${imageName}")
   withDockerRegistry([credentialsId: 'acr_auth', url: "https://${acr}"]) {
      app.push("${env.BRANCH_NAME}.${env.BUILD_NUMBER}")
                }
  }


 stage ("Deploy Application on Azure Kubernetes Service")
 {
  switch (env.BRANCH_NAME) {
    // Roll out to canary environment
    case "canary":
        sh("kubectl get ns ${appName}-${env.BRANCH_NAME} || kubectl create ns ${appName}-${env.BRANCH_NAME}")
        withCredentials([usernamePassword(credentialsId: 'acr_auth', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
          sh "kubectl -n ${appName}-${env.BRANCH_NAME} get secret acr-auth || kubectl --namespace=${appName}-${env.BRANCH_NAME} create secret docker-registry secret --docker-server ${acr} --docker-username $USERNAME --docker-password $PASSWORD"
        }
        // Change deployed image in canary to the one we just built
        sh("sed -i.bak 's#${appRepo}#${imageTag}#' ./canary/*.yaml")
        sh("sudo -s kubectl --kubeconfig ~admin12/.kube/config --namespace=canary apply -f ./services/")
        sh("sudo -s kubectl --kubeconfig ~admin12/.kube/config --namespace=canary apply -f ./canary/")
        sh("echo http://`kubectl --namespace=production get service/${appName} --output=json | jq -r '.status.loadBalancer.ingress[0].ip'` > ${appName}")
        break

    // Roll out to production
    case "master":
        // Change deployed image in master to the one we just built
        sh("sed -i.bak 's#${appRepo}#${imageTag}#' ./production/*.yaml")
        sh("sudo -s kubectl --kubeconfig ~admin12/.kube/config --namespace=canary apply -f ./services/")
        sh("sudo -s kubectl --kubeconfig ~admin12/.kube/config --namespace=canary apply -f ./production/")
        sh("echo http://`kubectl --namespace=psrestapi-production get service/${appName} --output=json | jq -r '.status.loadBalancer.ingress[0].ip'` > ${appName}")
        break
    
      case "release":
        sh("kubectl get ns ${appName}-${env.BRANCH_NAME} || kubectl create ns ${appName}-${env.BRANCH_NAME}")
        withCredentials([usernamePassword(credentialsId: 'acr_auth', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
          sh "kubectl -n ${appName}-${env.BRANCH_NAME} get secret acr-auth || kubectl --namespace=${appName}-${env.BRANCH_NAME} create secret docker-registry secret --docker-server ${acr} --docker-username $USERNAME --docker-password $PASSWORD"
        }
        // Change deployed image in master to the one we just built
        sh("sed -i.bak 's#${appRepo}#${imageTag}#' ./production/*.yaml")
        sh("sudo -s kubectl --kubeconfig ~admin12/.kube/config --namespace=canary apply -f ./services/")
        sh("sudo -s kubectl --kubeconfig ~admin12/.kube/config --namespace=canary apply -f ./production/")
        sh("echo http://`kubectl --namespace=psrestapi-production get service/${appName} --output=json | jq -r '.status.loadBalancer.ingress[0].ip'` > ${appName}")
        break

    // Roll out a dev environment
    default:
        // Create namespace if it doesn't exist
        sh("kubectl get ns ${appName}-${env.BRANCH_NAME} || kubectl create ns ${appName}-${env.BRANCH_NAME}")
        withCredentials([usernamePassword(credentialsId: 'acr_auth', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
          sh "kubectl -n ${appName}-${env.BRANCH_NAME} get secret acr-auth || kubectl --namespace=${appName}-${env.BRANCH_NAME} create secret docker-registry secret --docker-server ${acr} --docker-username $USERNAME --docker-password $PASSWORD"
        }  
        sh("sed -i.bak 's#${appRepo}#${imageTag}#' ./dev/*.yaml")
        sh("sudo -s kubectl --kubeconfig ~admin12/.kube/config --namespace=${appName}-${env.BRANCH_NAME} apply -f whoami/dev/")
        echo 'To access your environment run `kubectl proxy`'
        echo "Then access your service via http://localhost:8001/api/v1/namespaces/${appName}-${env.BRANCH_NAME}/services/${appName}:80/proxy/"     
    }
  }
}
