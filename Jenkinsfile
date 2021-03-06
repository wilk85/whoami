node {
  def acr = 'acrdemo66.azurecr.io'
  def appName = 'dockerimage'
  def imageName = "${acr}/${appName}"
  def imageTag = "${imageName}:${env.BRANCH_NAME}.${env.BUILD_NUMBER}"
  def appRepo = "acrdemo66.azurecr.io/dockerimage:v1.0"
  def nSpace1 = "production"
  def nSpace2 = "stage"
  def nSpace3 = "dev"

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
        sh("kubectl get ns ${nSpace1} || sudo -s kubectl create ns ${nSpace1}")
        // Change deployed image in canary to the one we just built
        sh("kubectl --namespace=${nSpace1} apply -f ./services/serviceCanary.yaml")
        sh("sed -i.bak 's#${appRepo}#${imageTag}#' ./canary/*.yaml")
        sh("sudo -s kubectl --kubeconfig ~admin12/.kube/config --namespace=${nSpace1} apply -f ./canary/")
        sh("echo http://`kubectl --namespace=${nSpace1} get service/${appName} --output=json | jq -r '.status.loadBalancer.ingress[0].ip'` > ${appName}")
        break

    // Roll out to production
    case "master":
        sh("kubectl get ns ${nSpace1} || sudo -s kubectl create ns ${nSpace1}")
        // Change deployed image in master to the one we just built
        sh("kubectl --namespace=${nSpace1} apply -f ./services/service.yaml")
        sh("sed -i.bak 's#${appRepo}#${imageTag}#' ./production/*.yaml")
        sh("sudo -s kubectl --kubeconfig ~admin12/.kube/config --namespace=${nSpace1} apply -f ./production/")
        sh("echo http://`kubectl --namespace=${nSpace1} get service/${appName} --output=json | jq -r '.status.loadBalancer.ingress[0].ip'` > ${appName}")
        break
    
    case "release":
        sh("kubectl get ns ${nSpace2} || sudo -s kubectl create ns ${nSpace2}")
        // Change deployed image in master to the one we just built
        sh("kubectl --namespace=${nSpace2} apply -f ./services/serviceCanary.yaml")
        sh("sed -i.bak 's#${appRepo}#${imageTag}#' ./release/*.yaml")
        sh("sudo -s kubectl --kubeconfig ~admin12/.kube/config --namespace=${nSpace2} apply -f ./release/")
        sh("echo http://`kubectl --namespace=${nSpace2} get service/${appName} --output=json | jq -r '.status.loadBalancer.ingress[0].ip'` > ${appName}")
        break
      
    case "dev":
        sh("kubectl get ns ${nSpace3} || sudo -s kubectl create ns ${nSpace3}")
        // Change deployed image in master to the one we just built
        sh("kubectl --namespace=${nSpace3} apply -f ./services/serviceCanary.yaml")
        sh("sed -i.bak 's#${appRepo}#${imageTag}#' ./dev/*.yaml")
        sh("sudo -s kubectl --kubeconfig ~admin12/.kube/config --namespace=${nSpace3} apply -f ./dev/")
        sh("echo http://`kubectl --namespace=${nSpace3} get service/${appName} --output=json | jq -r '.status.loadBalancer.ingress[0].ip'` > ${appName}")
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
