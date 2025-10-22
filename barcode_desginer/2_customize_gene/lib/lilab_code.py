
# 函数：获取基因序列（支持重试）
def get_gene_sequence(genbank_id, gene_name, external_name,max_retries=3):
    """
    从GenBank获取指定基因的序列（带重试机制）
    
    参数:
        genbank_id: GenBank ID
        gene_name: 基因名称
        max_retries: 最大重试次数
    
    返回:
        dict: 包含序列信息和状态的字典
    """
    import tqdm as tqdm
    for attempt in range(1, max_retries + 1):
        try:
            # 获取GenBank记录
            handle = Entrez.efetch(db="nuccore", id=genbank_id, rettype="gb")
            record = SeqIO.read(handle, "genbank")
            handle.close()
            
            # 遍历特征寻找目标基因
            for feature in record.features:
                if feature.type == "CDS":
                    product = feature.qualifiers.get("product", [""])[0]
                    if gene_name.lower() in product.lower():
                        start = int(feature.location.start)
                        end = int(feature.location.end)
                        sequence = str(record.seq[start:end])
                        return {
                            "status": "success",
                            "seq": sequence,
                            "external_name":external_name,
                            "genbank_id": genbank_id,
                            "gene_name": gene_name,
                            # "biotype":"protein_coding",
                            "length": len(sequence),
                            "start": start,
                            "end": end
                        }
            
            # 如果未找到匹配的基因
            return {
                "status": "not_found",
                "message": f"Gene '{gene_name}' not found in {genbank_id}"
            }
            
        except Exception as e:
            error_msg = f"Attempt {attempt} failed for {gene_name}({genbank_id}): {str(e)}"
            if attempt < max_retries:
                time.sleep(1)  # 重试前等待
                continue
            return {
                "status": "error",
                "message": error_msg
            }




# 主处理函数（与Ensembl代码格式一致）
def process_genes(gene_info, output_dir):
    """
    批量处理基因数据（参考Ensembl代码格式）
    
    参数:
        gene_info: 包含基因信息的DataFrame
        output_dir: 输出目录
    """
    import tqdm as tqdm
    sequences_of_all = {}
    error_messages = {gene: [] for gene in gene_info['gene_name']}
    
    # 带进度条的处理循环
    with tqdm(total=len(gene_info), desc="Retrieving sequences", position=0) as pbar_total:
        for idx, row in gene_info.iterrows():
            genbank_id = row['genbank_id']
            gene_name = row['product'] ## 可能需要修改的地方
            external_name=row['gene_name']
            
            # 获取基因序列
            result = get_gene_sequence(genbank_id, gene_name,external_name)
            
            # 处理结果
            if result['status'] == "success":
                sequences_of_all[gene_name] = {
                    "seq": result['seq'],
                    "external_name":result['external_name'],
                    "id": genbank_id,
                    "biotype":"protein_coding",
                    "length": result['length'],
                    "location": f"{result['start']}-{result['end']}"
                }
            else:
                error_messages[gene_name].append(result['message'])
                
            pbar_total.update(1)  # 更新主进度条
    
    # 输出错误信息
    for gene, messages in error_messages.items():
        if messages:
            for message in messages:
                print(f"ERROR: {message}")
    
    # 保存JSON结果
    output_file = os.path.join(output_dir, 'sequence_of_all_ex.json')
    with open(output_file, 'w') as f:
        json.dump(sequences_of_all, f, indent=2)
    
    print(f"\n处理完成！结果已保存至: {output_file}")

