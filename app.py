import os
from aws_cdk import App
from my_cdk_project.my_cdk_project_stack import my_cdk_project  # Asegúrate de que la ruta de importación sea correcta

app = App()

# Creando la instancia del stack y pasando los valores de entorno necesarios
my_cdk_project(app, "PruebaInstanciaPython", env={
    'account': '374889461091',  # ID de la cuenta AWS
    'region': os.getenv('CDK_DEFAULT_REGION')  # La región de AWS se obtiene de las variables de entorno
})

app.synth()  # Genera la plantilla de CloudFormation