## 处理Nikon扫描大图对应小图
## 处理的前置图像需要使用fiji分开channel

# 目前的文件名 tile_x001_y001_z001_0001.tif
# 文件名模板 C001-T0001-cy3-Z000.tif 
rm(list = ls())
channel=c('0001','0002','0003','0004') # 确定通道编号和信号之间的对应关系
color=c('FAM','DAPI','cy5','TxRed')
info=data.frame(channel,color)
head(info)

# 替换tile为C001--------------------------------------------------------------------------------------------------1
setwd("D:/3_PRISM/20251015_lilab_nikon_pic_split/cyc_001/")
for(file in list.files(pattern="\\.tif$", full.names=TRUE)) {
  new_name <- gsub("tile", "C001-", basename(file))
  file.rename(file, file.path(dirname(file), new_name))}

# x-1
# 极简版本
files <- list.files(pattern = ".*x\\d+.*\\.tif$")
for (f in files) {
  x_val <- as.numeric(gsub(".*x(\\d+).*", "\\1", f))
  new_name <- gsub("x\\d+", sprintf("x%03d", x_val-2), f)
  file.rename(f, new_name)
}

# 添加中间值N--------------------------------------------------------------------------------------------------2
# 批量重命名tif文件
rename_tif_files <- function(folder_path) {
  files <- list.files(folder_path, pattern = "\\.tif$")
  if (length(files) == 0) return("未找到tif文件")
  # 提取x值并计算最大值
  x_vals <- as.numeric(gsub(".*x(\\d+).*", "\\1", files))
  x_max <- max(x_vals)
  # 重命名文件
  for (file in files) {
    if (grepl("x\\d+", file)) {
      x <- as.numeric(gsub(".*x(\\d+).*", "\\1", file))
      n <- sprintf("N%03d", x_max + 1 - x)
      
      # 在第一个-后面，第一个_前面插入N值
      new_name <- sub("(-)([^_]*)(_)", paste0("\\1", n, "_\\2\\3"), file)
      
      # 执行重命名
      file.rename(file.path(folder_path, file), file.path(folder_path, new_name))
      cat("重命名:", file, "->", new_name, "\n")
    }
  }
  return(paste("完成", length(files), "个文件重命名"))
}
# 使用示例
rename_tif_files("./")

# 添加序号T--------------------------------------------------------------------------------------------------3
files <- list.files(pattern = "C001-.*\\.tif$")
for(f in files) {
  n <- as.numeric(gsub(".*N(\\d+).*", "\\1", f))
  y <- as.numeric(gsub(".*y(\\d+).*", "\\1", f))
  x_vals <- as.numeric(gsub(".*x(\\d+).*", "\\1", files))
  x_max <- max(x_vals)
  t_val <- sprintf("T%04d_", n + (y-1)*x_max)
  file.rename(f, sub("C001-", paste0("C001-", t_val), f))
}

# 删除N X Y 信息--------------------------------------------------------------------------------------------------4
# 批量重命名tif文件 - 删除N、x和y部分
rename_tif_files <- function(folder_path) {
  files <- list.files(folder_path, pattern = "\\.tif$")
  for (file in files) {
    # 删除N部分、x部分和y部分
    new_name <- gsub("_N\\d+__x\\d+_y\\d+_", "_", file)
    file.rename(file.path(folder_path, file), file.path(folder_path, new_name))
  }
  return(paste("完成", length(files), "个文件重命名"))
}

# 使用示例
rename_tif_files("./")

# Z修改大小写--------------------------------------------------------------------------------------------------5
# 批量重命名tif文件 - 将z改为Z并将z后的数值减1
rename_tif_files <- function(folder_path) {
  files <- list.files(folder_path, pattern = "\\.tif$")
  for (file in files) {
    z_value <- as.numeric(gsub(".*z(\\d{3}).*", "\\1", file))
    new_name <- gsub("z\\d{3}", sprintf("Z%03d", z_value-1), file)
    file.rename(file.path(folder_path, file), file.path(folder_path, new_name))
  }
  return(paste("完成", length(files), "个文件重命名"))
}

# 使用示例
rename_tif_files("./")
# 修改通道信息--------------------------------------------------------------------------------------------------6
# 批量重命名tif文件
rename_tif_files <- function(folder_path) {
  files <- list.files(folder_path, pattern = "\\.tif$")
  for (file in files) {
    file_num <- gsub(".*-(\\d{4})\\.tif$", "\\1", file)
    color_name <- info$color[info$channel == file_num]
    if (length(color_name) > 0) {
      new_name <- gsub("\\d{4}\\.tif$", paste0(color_name, ".tif"), file)
      file.rename(file.path(folder_path, file), file.path(folder_path, new_name))
    }
  }
}
rename_tif_files("./")

# 调整文件名顺序--------------------------------------------------------------------------------------------------7
# 交换文件名中的最后一位和第三位内容
swap_filename_parts <- function(folder_path) {
  files <- list.files(folder_path, pattern = "\\.tif$")
  for (file in files) {
    # 使用正则表达式匹配文件名各部分
    # 模式：C001-T0001_Z000-cy5.tif
    pattern <- "^(C\\d+)-(T\\d+)_(Z\\d+)-([a-zA-Z0-9]+)\\.tif$"
    if (grepl(pattern, file)) {
      # 提取各部分
      prefix <- gsub(pattern, "\\1", file)  # C001
      t_part <- gsub(pattern, "\\2", file)  # T0001
      z_part <- gsub(pattern, "\\3", file)  # Z000
      channel <- gsub(pattern, "\\4", file) # cy5
      
      # 交换最后一位和第三位
      new_name <- paste0(prefix, "-", t_part, "_", channel, "-", z_part, ".tif")
      
      # 执行重命名
      file.rename(file.path(folder_path, file), file.path(folder_path, new_name))
      cat("重命名:", file, "->", new_name, "\n")
    }
  }
}
# 使用示例
swap_filename_parts("./")

# 修改文件名中的_--------------------------------------------------------------------------------------------------8
# 将文件名中的所有_替换为-
replace_dashes <- function(folder_path) {
  files <- list.files(folder_path, pattern = "\\.tif$")
  for (file in files) {
    new_name <- gsub("_", "-", file)
    file.rename(file.path(folder_path, file), file.path(folder_path, new_name))
  }
}
replace_dashes("./")

















