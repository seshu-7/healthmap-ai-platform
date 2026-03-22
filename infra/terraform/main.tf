terraform {
  required_version = ">= 1.5"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
  backend "s3" { bucket = "healthmap-terraform-state"; key = "infra/terraform.tfstate"; region = "us-east-1" }
}

provider "aws" { region = var.aws_region }

variable "aws_region"        { default = "us-east-1" }
variable "environment"       { default = "production" }
variable "cluster_name"      { default = "healthmap-ai-platform" }
variable "node_instance_type" { default = "t3.large" }
variable "node_desired_count" { default = 3 }
variable "db_instance_class"  { default = "db.t3.medium" }
variable "db_password"        { sensitive = true }

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"; version = "~> 5.0"
  name = "${var.cluster_name}-vpc"; cidr = "10.0.0.0/16"
  azs = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  enable_nat_gateway = true; single_nat_gateway = var.environment != "production"
  enable_dns_hostnames = true
  public_subnet_tags  = { "kubernetes.io/role/elb" = 1 }
  private_subnet_tags = { "kubernetes.io/role/internal-elb" = 1 }
  tags = { Environment = var.environment, Project = "healthmap" }
}

module "eks" {
  source = "terraform-aws-modules/eks/aws"; version = "~> 20.0"
  cluster_name = var.cluster_name; cluster_version = "1.29"
  vpc_id = module.vpc.vpc_id; subnet_ids = module.vpc.private_subnets
  cluster_endpoint_public_access = true
  eks_managed_node_groups = {
    general = { instance_types = [var.node_instance_type]; min_size = 2; max_size = 6; desired_size = var.node_desired_count; labels = { workload = "general" } }
    ai-agents = { instance_types = ["t3.xlarge"]; min_size = 1; max_size = 4; desired_size = 2; labels = { workload = "ai-agents" }
      taints = [{ key = "ai-workload", value = "true", effect = "NO_SCHEDULE" }] }
  }
  tags = { Environment = var.environment }
}

resource "aws_ecr_repository" "ai" { name = "healthmap/ai-agent-service"; image_scanning_configuration { scan_on_push = true } }
resource "aws_ecr_repository" "gw" { name = "healthmap/api-gateway"; image_scanning_configuration { scan_on_push = true } }

resource "aws_db_subnet_group" "db" { name = "${var.cluster_name}-db"; subnet_ids = module.vpc.private_subnets }
resource "aws_security_group" "rds" {
  name_prefix = "${var.cluster_name}-rds-"; vpc_id = module.vpc.vpc_id
  ingress { from_port = 5432; to_port = 5432; protocol = "tcp"; security_groups = [module.eks.node_security_group_id] }
}
resource "aws_db_instance" "db" {
  identifier = "${var.cluster_name}-db"; engine = "postgres"; engine_version = "16.1"
  instance_class = var.db_instance_class; allocated_storage = 50
  db_name = "healthmap"; username = "healthmap_admin"; password = var.db_password
  vpc_security_group_ids = [aws_security_group.rds.id]; db_subnet_group_name = aws_db_subnet_group.db.name
  backup_retention_period = 7; multi_az = var.environment == "production"
  skip_final_snapshot = var.environment != "production"; storage_encrypted = true
}

output "cluster_endpoint" { value = module.eks.cluster_endpoint }
output "ecr_ai_url" { value = aws_ecr_repository.ai.repository_url }
output "ecr_gw_url" { value = aws_ecr_repository.gw.repository_url }
output "rds_endpoint" { value = aws_db_instance.db.endpoint }
