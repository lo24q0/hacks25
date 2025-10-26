import logging
import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class GCodeTo3MFConverter:
    """
    G-code到3MF文件格式转换器
    
    实现将标准G-code文件转换为Bambu Lab兼容的3MF格式。
    3MF是基于ZIP的容器格式,包含XML元数据和G-code内容。
    """

    # 3MF命名空间
    NAMESPACES = {
        '': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02',
        'p': 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06',
        'b': 'http://schemas.bambulab.com/package/2021/01'
    }

    def __init__(self):
        """
        初始化转换器
        """
        self._register_namespaces()

    def _register_namespaces(self):
        """
        注册XML命名空间
        """
        for prefix, uri in self.NAMESPACES.items():
            if prefix:
                ET.register_namespace(prefix, uri)

    def convert(
        self,
        gcode_path: str,
        output_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        将G-code文件转换为3MF格式
        
        Args:
            gcode_path: G-code文件路径
            output_path: 输出3MF文件路径
            metadata: 可选的元数据字典,包含打印机配置等信息
            
        Returns:
            str: 输出文件的实际路径
            
        Raises:
            FileNotFoundError: 如果G-code文件不存在
            RuntimeError: 如果转换失败
        """
        if not os.path.exists(gcode_path):
            raise FileNotFoundError(f"G-code file not found: {gcode_path}")

        try:
            logger.info(f"Converting G-code to 3MF: {gcode_path} -> {output_path}")
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 确保输出文件有正确的扩展名
            if not output_path.endswith('.3mf'):
                output_path = output_path + '.3mf'
            
            # 读取G-code内容
            with open(gcode_path, 'r', encoding='utf-8') as f:
                gcode_content = f.read()
            
            # 创建3MF ZIP容器
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 1. 添加[Content_Types].xml
                zf.writestr('[Content_Types].xml', self._create_content_types())
                
                # 2. 添加_rels/.rels
                zf.writestr('_rels/.rels', self._create_relationships())
                
                # 3. 添加3D/3dmodel.model (主3D模型文件)
                zf.writestr('3D/3dmodel.model', self._create_3d_model(metadata))
                
                # 4. 添加Metadata/model_settings.config (Bambu特定配置)
                zf.writestr('Metadata/model_settings.config', 
                           self._create_model_settings(metadata))
                
                # 5. 添加Metadata/plate_1.gcode (实际G-code内容)
                zf.writestr('Metadata/plate_1.gcode', gcode_content)
                
                # 6. 添加缩略图(如果提供)
                if metadata and 'thumbnail_path' in metadata:
                    thumbnail_path = metadata['thumbnail_path']
                    if os.path.exists(thumbnail_path):
                        with open(thumbnail_path, 'rb') as thumb:
                            zf.writestr('Metadata/plate_1.png', thumb.read())
            
            logger.info(f"Successfully converted to 3MF: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to convert G-code to 3MF: {e}")
            raise RuntimeError(f"Conversion failed: {e}")

    def _create_content_types(self) -> str:
        """
        创建[Content_Types].xml文件
        
        定义3MF容器中各文件类型的MIME类型
        
        Returns:
            str: XML内容
        """
        root = ET.Element('Types', {
            'xmlns': 'http://schemas.openxmlformats.org/package/2006/content-types'
        })
        
        # 默认类型
        ET.SubElement(root, 'Default', {
            'Extension': 'rels',
            'ContentType': 'application/vnd.openxmlformats-package.relationships+xml'
        })
        ET.SubElement(root, 'Default', {
            'Extension': 'model',
            'ContentType': 'application/vnd.ms-package.3dmanufacturing-3dmodel+xml'
        })
        ET.SubElement(root, 'Default', {
            'Extension': 'png',
            'ContentType': 'image/png'
        })
        ET.SubElement(root, 'Default', {
            'Extension': 'gcode',
            'ContentType': 'text/x.gcode'
        })
        ET.SubElement(root, 'Default', {
            'Extension': 'config',
            'ContentType': 'text/xml'
        })
        
        return self._prettify_xml(root)

    def _create_relationships(self) -> str:
        """
        创建_rels/.rels关系文件
        
        定义包内各部分之间的关系
        
        Returns:
            str: XML内容
        """
        root = ET.Element('Relationships', {
            'xmlns': 'http://schemas.openxmlformats.org/package/2006/relationships'
        })
        
        # 指向3D模型的关系
        ET.SubElement(root, 'Relationship', {
            'Target': '/3D/3dmodel.model',
            'Id': 'rel0',
            'Type': 'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'
        })
        
        return self._prettify_xml(root)

    def _create_3d_model(self, metadata: Optional[Dict[str, Any]]) -> str:
        """
        创建3D/3dmodel.model文件
        
        包含3D模型定义和构建信息
        
        Args:
            metadata: 元数据字典
            
        Returns:
            str: XML内容
        """
        # 创建根元素
        root = ET.Element('model', {
            'unit': 'millimeter',
            'xml:lang': 'en-US',
            'xmlns': self.NAMESPACES[''],
            'xmlns:p': self.NAMESPACES['p']
        })
        
        # 元数据
        metadata_elem = ET.SubElement(root, 'metadata', {'name': 'Application'})
        metadata_elem.text = metadata.get('application', 'BambuStudio') if metadata else 'BambuStudio'
        
        # 资源部分(空的,因为我们直接使用G-code)
        resources = ET.SubElement(root, 'resources')
        
        # 构建部分
        build = ET.SubElement(root, 'build')
        
        return self._prettify_xml(root)

    def _create_model_settings(self, metadata: Optional[Dict[str, Any]]) -> str:
        """
        创建Metadata/model_settings.config文件
        
        包含Bambu特定的打印配置
        
        Args:
            metadata: 元数据字典
            
        Returns:
            str: XML内容
        """
        root = ET.Element('config')
        
        # 打印机型号
        printer_model = ET.SubElement(root, 'printer')
        printer_model.text = metadata.get('printer_model', 'Bambu Lab H2D') if metadata else 'Bambu Lab H2D'
        
        # 打印设置
        if metadata:
            # 层高
            if 'layer_height' in metadata:
                layer_height = ET.SubElement(root, 'layer_height')
                layer_height.text = str(metadata['layer_height'])
            
            # 填充率
            if 'infill_density' in metadata:
                infill = ET.SubElement(root, 'fill_density')
                infill.text = str(metadata['infill_density'])
            
            # 打印速度
            if 'print_speed' in metadata:
                speed = ET.SubElement(root, 'print_speed')
                speed.text = str(metadata['print_speed'])
            
            # 支撑
            if 'support_enabled' in metadata:
                support = ET.SubElement(root, 'support')
                support.text = 'true' if metadata['support_enabled'] else 'false'
            
            # 材料类型
            if 'material_type' in metadata:
                material = ET.SubElement(root, 'filament_type')
                material.text = str(metadata['material_type'])
            
            # 喷嘴温度
            if 'nozzle_temperature' in metadata:
                nozzle_temp = ET.SubElement(root, 'nozzle_temperature')
                nozzle_temp.text = str(metadata['nozzle_temperature'])
            
            # 热床温度
            if 'bed_temperature' in metadata:
                bed_temp = ET.SubElement(root, 'bed_temperature')
                bed_temp.text = str(metadata['bed_temperature'])
        
        # 生成时间
        timestamp = ET.SubElement(root, 'timestamp')
        timestamp.text = datetime.now().isoformat()
        
        return self._prettify_xml(root)

    def _prettify_xml(self, elem: ET.Element) -> str:
        """
        格式化XML为易读格式
        
        Args:
            elem: XML元素
            
        Returns:
            str: 格式化的XML字符串
        """
        # 添加XML声明
        xml_str = ET.tostring(elem, encoding='utf-8', method='xml')
        return b'<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str

    def extract_gcode_from_3mf(self, mf_path: str, output_path: str) -> str:
        """
        从3MF文件中提取G-code
        
        Args:
            mf_path: 3MF文件路径
            output_path: 输出G-code文件路径
            
        Returns:
            str: 输出G-code文件路径
            
        Raises:
            FileNotFoundError: 如果3MF文件不存在
            RuntimeError: 如果提取失败
        """
        if not os.path.exists(mf_path):
            raise FileNotFoundError(f"3MF file not found: {mf_path}")
        
        try:
            logger.info(f"Extracting G-code from 3MF: {mf_path} -> {output_path}")
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with zipfile.ZipFile(mf_path, 'r') as zf:
                # 查找G-code文件(通常在Metadata/plate_1.gcode)
                gcode_files = [f for f in zf.namelist() if f.endswith('.gcode')]
                
                if not gcode_files:
                    raise RuntimeError("No G-code file found in 3MF archive")
                
                # 提取第一个G-code文件
                gcode_content = zf.read(gcode_files[0])
                
                # 写入输出文件
                with open(output_path, 'wb') as f:
                    f.write(gcode_content)
            
            logger.info(f"Successfully extracted G-code: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to extract G-code from 3MF: {e}")
            raise RuntimeError(f"Extraction failed: {e}")

    def validate_3mf(self, mf_path: str) -> bool:
        """
        验证3MF文件是否有效
        
        Args:
            mf_path: 3MF文件路径
            
        Returns:
            bool: 文件是否有效
        """
        try:
            if not os.path.exists(mf_path):
                return False
            
            with zipfile.ZipFile(mf_path, 'r') as zf:
                # 检查必需的文件
                required_files = ['[Content_Types].xml', '_rels/.rels']
                namelist = zf.namelist()
                
                for required in required_files:
                    if required not in namelist:
                        logger.warning(f"Missing required file: {required}")
                        return False
                
                # 检查是否有3D模型或G-code
                has_model = any(f.endswith('.model') for f in namelist)
                has_gcode = any(f.endswith('.gcode') for f in namelist)
                
                if not (has_model or has_gcode):
                    logger.warning("No 3D model or G-code found")
                    return False
                
                return True
                
        except zipfile.BadZipFile:
            logger.warning(f"Invalid ZIP archive: {mf_path}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
