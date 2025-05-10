FROM nginx:alpine

# Copia o arquivo de configuração customizado
COPY nginx.conf /etc/nginx/nginx.conf
