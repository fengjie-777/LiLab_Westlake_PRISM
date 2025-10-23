//open("D:/3_PRISM/20251011_Lilab_Nikon_pic_data/single/tile_x001_y001_z001.tif");
//selectImage("tile_x001_y001_z001.tif");
//run("Stack to Images");
//run("Tiff...");
//saveAs("Tiff", "D:/3_PRISM/20251011_Lilab_Nikon_pic_split_data/tile_x001_y001_z001-0004.tif");
//close;
//saveAs("Tiff", "D:/3_PRISM/20251011_Lilab_Nikon_pic_split_data/tile_x001_y001_z001-0003.tif");
//close;
//saveAs("Tiff", "D:/3_PRISM/20251011_Lilab_Nikon_pic_split_data/tile_x001_y001_z001-0002.tif");
//close;
//saveAs("Tiff", "D:/3_PRISM/20251011_Lilab_Nikon_pic_split_data/tile_x001_y001_z001-0001.tif");
//selectImage("tile_x001_y001_z001-0001.tif");
//close;

// 配置输入输出路径
inputDir = "D:/20251014nikon/small/";
outputDir = "D:/20251014nikon/small_split/";
//inputDir = "D:/3_PRISM/20251011_Lilab_PRISM_Nikon_Matlab_cidre_test1_processed/test1/";
//outputDir = "D:/3_PRISM/20251011_Lilab_PRISM_Nikon_Matlab_cidre_test1_processed/test1_output/";
// 获取所有TIF文件
fileList = getFileList(inputDir);
for (i = 0; i < fileList.length; i++) {
    // 只处理以"tile"开头的TIF文件
    if (endsWith(fileList[i], ".tif") && startsWith(fileList[i], "tile")) {
        // 打开当前堆栈图像
        filePath = inputDir + fileList[i];
        open(filePath);
        // 替代File.nameWithoutExtension的方法
        // 方法1: 使用字符串处理去除扩展名
        fullName = fileList[i];
        dotIndex = lastIndexOf(fullName, ".");
        if (dotIndex > 0) {
            fileName = substring(fullName, 0, dotIndex);
        } else {
            fileName = fullName; // 如果没有扩展名，使用全名
        }
        // 直接拆分堆栈为4个独立图像
        run("Stack to Images");
        // 处理拆分出的4个图像
        for (slice = 1; slice <= 4; slice++) {
            // 构建输出路径（使用您期望的命名格式）
            outputSliceTitle = fileName + "-000" + slice;
            selectImage(outputSliceTitle);
            outputPath = outputDir + outputSliceTitle+".tif";
            saveAs("Tiff", outputPath);
        }
        run("Close All");
    } // 这里添加了缺失的右大括号
}
print("所有堆栈图像处理完成！共处理 " + fileList.length + " 个文件");

