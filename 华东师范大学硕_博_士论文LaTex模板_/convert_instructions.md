# PlantUML图表转换说明

由于网络代理问题，无法自动转换PlantUML文件为PNG图片。请按照以下步骤手动转换：

## 方法1：使用在线PlantUML服务

1. 访问 http://www.plantuml.com/plantuml/
2. 将以下文件的内容复制到在线编辑器中：
   - `chapters/fig-0/microservice_deployment.puml`
   - `chapters/fig-0/data_management.puml`
   - `chapters/fig-0/monitoring_fault_tolerance.puml`
3. 点击"Submit"生成图片
4. 右键保存图片为对应的PNG文件名

## 方法2：使用本地PlantUML JAR

1. 确保已安装Java
2. 运行以下命令：
```bash
java -jar plantuml.jar -tpng chapters/fig-0/microservice_deployment.puml
java -jar plantuml.jar -tpng chapters/fig-0/data_management.puml
java -jar plantuml.jar -tpng chapters/fig-0/monitoring_fault_tolerance.puml
```

## 方法3：使用VS Code插件

1. 安装PlantUML插件
2. 打开.puml文件
3. 使用Ctrl+Shift+P打开命令面板
4. 选择"PlantUML: Export Current Diagram"
5. 选择PNG格式导出

## 生成的文件

转换完成后，应该生成以下PNG文件：
- `chapters/fig-0/microservice_deployment.png`
- `chapters/fig-0/data_management.png`
- `chapters/fig-0/monitoring_fault_tolerance.png`

这些文件将用于第五章的微服务架构实现节中。
