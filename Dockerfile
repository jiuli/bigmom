FROM python:3.6-rc

MAINTAINER jasonli 3131998116@qq.com

# ADD requirements.txt requirements.txt
# RUN pip3 install -r requirements.txt
# RUN pip3 install django

#RUN mkdir -p /opt/python-work
# 安装要的python包
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# 创建工作目录
RUN mkdir -p /opt/python-work/bigmom
# 指定工作目录
WORKDIR /opt/python-work/bigmom
# 挂载到该目录 便于代码更新上传到公共地方  
VOLUME /opt/python-work/bigmom

# 复制当前目录下所有到 /opt/python-work/bigmom
ADD run.sh /opt/python-work/bigmom
RUN chmod 777 run.sh

# 暴露端口
EXPOSE 8091

# 启动该项目容器用
CMD ["/bin/sh", "run.sh"]

# 设置变量
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
