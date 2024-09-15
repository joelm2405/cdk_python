from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    DefaultStackSynthesizer
)
from constructs import Construct

class my_cdk_project(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:  # Inicializador del stack con el sintetizador de CDK
        # Configuración del DefaultStackSynthesizer, que administra los recursos de activos de CloudFormation
        synthesizer = DefaultStackSynthesizer(
            file_assets_bucket_name="pruebacloudd",  # Nombre del bucket para los activos de archivos
            bucket_prefix="",  # Prefijo para organizar archivos en el bucket
            cloud_formation_execution_role="arn:aws:iam::374889461091:role/LabRole",  # Rol para ejecutar CloudFormation
            deploy_role_arn="arn:aws:iam::374889461091:role/LabRole",  # Rol de despliegue para la infraestructura
            file_asset_publishing_role_arn="arn:aws:iam::374889461091:role/LabRole",  # Rol para publicar los activos de archivo
            image_asset_publishing_role_arn="arn:aws:iam::374889461091:role/LabRole"  # Rol para publicar los activos de imagen
        )

        # Llamada a la clase base Stack, pasando el sintetizador
        super().__init__(scope, id, synthesizer=synthesizer, **kwargs)

        # Buscando una VPC existente mediante su ID
        vpc = ec2.Vpc.from_lookup(self, "ExistingVpc", vpc_id="vpc-0eb704c4b30fa3b0c")

        # Obteniendo un rol IAM existente desde su ARN
        instance_role = iam.Role.from_role_arn(
            self, "ExistingRole",
            role_arn="arn:aws:iam::374889461091:role/LabRole"
        )

        # Busca la última imagen de Ubuntu Focal 20.04 LTS en el catálogo de Amazon EC2
        ubuntu_ami = ec2.LookupMachineImage(
            name="ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*",  # Patrón de nombre de la imagen
            owners=["099720109477"]  # ID del propietario (Canonical)
        )

        # Creación de una instancia EC2 en la VPC especificada, con el tipo t2.micro y usando la imagen de Ubuntu
        instance = ec2.Instance(self, "WebServerInstance",
                                instance_type=ec2.InstanceType("t2.micro"),  # Tipo de instancia
                                machine_image=ubuntu_ami,  # Imagen de máquina que utilizará la instancia
                                vpc=vpc,  # VPC donde se lanzará la instancia
                                role=instance_role  # Rol IAM asociado a la instancia
                                )

        # Lista de comandos para configurar el servidor web (User Data)
        user_data_commands = [
            "sudo apt-get update -y",  # Actualiza los paquetes de software
            "sudo apt-get install -y apache2 git",  # Instala Apache y Git
            "sudo systemctl start apache2",  # Inicia el servicio de Apache
            "sudo systemctl enable apache2",  # Habilita Apache para que se inicie al arrancar
            "sudo echo 'Listen 8000' >> /etc/apache2/ports.conf",  # Configura Apache para escuchar en el puerto 8000
            "sudo echo 'Listen 8080' >> /etc/apache2/ports.conf",  # Configura Apache para escuchar en el puerto 8080
            "sudo git clone https://github.com/joelm2405/websimple.git /var/www/websimple",  # Clona el repositorio websimple
            "sudo git clone https://github.com/joelm2405/webplantilla.git /var/www/webplantilla",  # Clona el repositorio webplantilla
            # Configuración del host virtual para el sitio web en el puerto 8000
            "echo '<VirtualHost *:8000>' | sudo tee /etc/apache2/sites-available/websimple.conf",
            "echo '    DocumentRoot /var/www/websimple' | sudo tee -a /etc/apache2/sites-available/websimple.conf",
            "echo '    ErrorLog ${APACHE_LOG_DIR}/error.log' | sudo tee -a /etc/apache2/sites-available/websimple.conf",
            "echo '    CustomLog ${APACHE_LOG_DIR}/access.log combined' | sudo tee -a /etc/apache2/sites-available/websimple.conf",
            "echo '</VirtualHost>' | sudo tee -a /etc/apache2/sites-available/websimple.conf",
            # Configuración del host virtual para el sitio web en el puerto 8080
            "echo '<VirtualHost *:8080>' | sudo tee /etc/apache2/sites-available/webplantilla.conf",
            "echo '    DocumentRoot /var/www/webplantilla' | sudo tee -a /etc/apache2/sites-available/webplantilla.conf",
            "echo '    ErrorLog ${APACHE_LOG_DIR}/error.log' | sudo tee -a /etc/apache2/sites-available/webplantilla.conf",
            "echo '    CustomLog ${APACHE_LOG_DIR}/access.log combined' | sudo tee -a /etc/apache2/sites-available/webplantilla.conf",
            "echo '</VirtualHost>' | sudo tee -a /etc/apache2/sites-available/webplantilla.conf",
            "sudo a2ensite websimple",  # Habilita el sitio websimple
            "sudo a2ensite webplantilla",  # Habilita el sitio webplantilla
            "sudo systemctl restart apache2"  # Reinicia Apache para aplicar los cambios
        ]

        # Añadiendo los comandos de configuración al User Data de la instancia
        instance.user_data.add_commands(*user_data_commands)

        # Configuración de los permisos de red (Security Group) para permitir tráfico en puertos específicos
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(80), "Allow HTTP traffic on port 80")  # Permite HTTP en puerto 80
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(22), "Allow SSH traffic on port 22")  # Permite SSH en puerto 22
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(8000), "Allow HTTP traffic on port 8000")  # Permite HTTP en puerto 8000
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(8080), "Allow HTTP traffic on port 8080")  # Permite HTTP en puerto 8080
