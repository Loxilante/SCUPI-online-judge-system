import re
import subprocess
import os
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers
# Create your views here.
class JavaCompileSerializer(serializers.Serializer):
    dir = serializers.CharField(required=True)
    kb = serializers.FloatField(required=True)
    args = serializers.CharField(required=False, allow_blank=True)
    time_limit_in_ms = serializers.FloatField(required=True)
    stdin_data = serializers.CharField(required=False, allow_blank=True)
    

class javaView(APIView):
    
    def post(self, request):
        serializer = JavaCompileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        source_dir = os.getcwd() + "/files" +request.data.get('dir')
        limit_in_kb = request.data.get('kb')
        args = request.data.get('args')
        time_limit_in_ms = request.data.get('time_limit_in_ms')
        stdin_data = request.data.get('stdin_data')
        try:
            # 检查源文件目录是否存在
            if not os.path.exists(source_dir):
                return Response({"error":f"Source directory '{source_dir}' not found."}, status=status.HTTP_400_BAD_REQUEST)

            # 搜索 .java文件
            java_files = [os.path.join(source_dir, f) for f in os.listdir(source_dir) if f.endswith('.java')]

            if not java_files:
                return Response({"error":"No .java files found in the source directory."}, status=status.HTTP_400_BAD_REQUEST)

            # 构建编译命令
            compile_command = ["javac"] + java_files
            # 执行编译命令
            subprocess.run(compile_command, capture_output=True, text=True, check=True)

        except subprocess.CalledProcessError as cpe_error:
            return Response({"error":f"CE:{cpe_error}", "details":cpe_error.stderr},status=status.HTTP_400_BAD_REQUEST)
    
        try:
            output = subprocess.check_output([os.getcwd()+"/judge/excuting.exe", source_dir, args, stdin_data, str(time_limit_in_ms), str(limit_in_kb)], stderr=subprocess.STDOUT, text=True)
            output = re.findall(r"<-&(.*?)&->", output, re.DOTALL)
            

            # 打印输出和运行信息
            return Response({"Status":output[0],
                            "Runtime":output[1],
                            "Runspace":output[2],
                            "Output":output[3]},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error":f"An error occurred: {e}"},status=status.HTTP_400_BAD_REQUEST)
