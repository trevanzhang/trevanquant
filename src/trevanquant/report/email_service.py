"""
邮件发送服务
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional, Dict, Any
import jinja2

from ..utils.logger import get_logger
from ..utils.config import get_config

logger = get_logger(__name__)


class EmailService:
    """邮件发送服务"""

    def __init__(self):
        """初始化邮件服务"""
        self.config = get_config()
        self.email_config = self.config.email
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                Path(__file__).parent / "templates"
            )
        )

    def send_email(
        self,
        subject: str,
        content: str,
        recipients: List[str] = None,
        attachments: List[str] = None,
        html_content: bool = True
    ) -> Dict[str, Any]:
        """
        发送邮件

        Args:
            subject: 邮件主题
            content: 邮件内容
            recipients: 收件人列表
            attachments: 附件路径列表
            html_content: 是否为HTML格式

        Returns:
            Dict[str, Any]: 发送结果
        """
        try:
            # 设置收件人
            if not recipients:
                recipients = self.email_config.recipients

            if not recipients:
                return {'success': False, 'error': '没有配置收件人'}

            logger.info(f"开始发送邮件: {subject} 到 {len(recipients)} 个收件人")

            # 创建邮件对象
            if html_content:
                msg = MIMEMultipart('alternative')
            else:
                msg = MIMEMultipart()

            # 设置邮件头
            msg['From'] = self.email_config.sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject

            # 添加邮件内容
            if html_content:
                # HTML内容
                html_part = MIMEText(content, 'html', 'utf-8')
                msg.attach(html_part)

                # 也添加文本版本
                text_content = self._html_to_text(content)
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            else:
                text_part = MIMEText(content, 'plain', 'utf-8')
                msg.attach(text_part)

            # 添加附件
            if attachments:
                for attachment_path in attachments:
                    self._add_attachment(msg, attachment_path)

            # 发送邮件
            result = self._send_email(msg, recipients)

            logger.info(f"邮件发送完成: {result}")
            return result

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return {'success': False, 'error': str(e)}

    def send_template_email(
        self,
        template_name: str,
        subject: str,
        template_data: Dict[str, Any],
        recipients: List[str] = None,
        attachments: List[str] = None
    ) -> Dict[str, Any]:
        """
        发送模板邮件

        Args:
            template_name: 模板名称
            subject: 邮件主题
            template_data: 模板数据
            recipients: 收件人列表
            attachments: 附件路径列表

        Returns:
            Dict[str, Any]: 发送结果
        """
        try:
            # 加载模板
            template = self.template_env.get_template(template_name)

            # 渲染模板
            html_content = template.render(**template_data)

            # 发送邮件
            return self.send_email(
                subject=subject,
                content=html_content,
                recipients=recipients,
                attachments=attachments,
                html_content=True
            )

        except Exception as e:
            logger.error(f"模板邮件发送失败: {e}")
            return {'success': False, 'error': str(e)}

    def _send_email(self, msg: MIMEMultipart, recipients: List[str]) -> Dict[str, Any]:
        """
        实际发送邮件

        Args:
            msg: 邮件对象
            recipients: 收件人列表

        Returns:
            Dict[str, Any]: 发送结果
        """
        try:
            # 创建SMTP连接
            server = smtplib.SMTP(
                self.email_config.smtp_server,
                self.email_config.smtp_port
            )

            # 启用安全传输
            server.starttls()

            # 登录
            server.login(
                self.email_config.sender_email,
                self.email_config.sender_password
            )

            # 发送邮件
            text = msg.as_string()
            server.sendmail(self.email_config.sender_email, recipients, text)

            # 关闭连接
            server.quit()

            return {
                'success': True,
                'message': '邮件发送成功',
                'recipients': recipients
            }

        except Exception as e:
            logger.error(f"SMTP发送失败: {e}")
            return {'success': False, 'error': f"SMTP发送失败: {e}"}

    def _add_attachment(self, msg: MIMEMultipart, file_path: str) -> None:
        """
        添加附件

        Args:
            msg: 邮件对象
            file_path: 附件文件路径
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"附件文件不存在: {file_path}")
                return

            # 根据文件类型选择处理方式
            if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                # 图片附件
                with open(path, 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data)
                    image.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{path.name}"'
                    )
                    msg.attach(image)
            else:
                # 其他文件附件
                with open(path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{path.name}"'
                    )
                    msg.attach(part)

            logger.info(f"添加附件: {file_path}")

        except Exception as e:
            logger.error(f"添加附件失败 {file_path}: {e}")

    def _html_to_text(self, html_content: str) -> str:
        """
        简单的HTML转文本

        Args:
            html_content: HTML内容

        Returns:
            str: 转换后的文本内容
        """
        import re

        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', html_content)

        # 处理换行
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')

        # 清理多余空白
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()

        return text

    def test_connection(self) -> Dict[str, Any]:
        """
        测试邮件连接

        Returns:
            Dict[str, Any]: 测试结果
        """
        try:
            logger.info("测试邮件连接...")

            # 创建SMTP连接
            server = smtplib.SMTP(
                self.email_config.smtp_server,
                self.email_config.smtp_port
            )

            # 启用安全传输
            server.starttls()

            # 尝试登录
            server.login(
                self.email_config.sender_email,
                self.email_config.sender_password
            )

            # 关闭连接
            server.quit()

            logger.info("邮件连接测试成功")
            return {'success': True, 'message': '邮件连接正常'}

        except Exception as e:
            logger.error(f"邮件连接测试失败: {e}")
            return {'success': False, 'error': str(e)}


# 创建全局邮件服务实例
email_service = EmailService()