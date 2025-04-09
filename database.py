from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Text, text, BigInteger, ForeignKey
from contextlib import asynccontextmanager
from logger import info, error
from config import DATABASE_URL


# 基础模型类 - SQLAlchemy的声明式基类，所有数据库模型都继承自此类
class Base(DeclarativeBase):
    pass


# 账号模型 - 存储Cursor账号信息
class AccountModel(Base):
    __tablename__ = "accounts"  # 表名
    
    # 邮箱作为主键，用于唯一标识一个账号
    email = Column(String, primary_key=True)
    
    # 用户名，不可为空
    user = Column(String, nullable=False)
    
    # 密码，可以为空（某些认证方式可能不需要密码）
    password = Column(String, nullable=True)
    
    # 认证令牌，用于API调用，不可为空
    token = Column(String, nullable=False)
    
    # 使用限制信息，存储为JSON格式的文本
    usage_limit = Column(Text, nullable=True)
    
    # 创建时间，存储为文本格式
    created_at = Column(Text, nullable=True)
    
    # 账号状态，默认为"active"，表示账号可用
    status = Column(String, default="active", nullable=False)
    
    # 账号ID（毫秒时间戳），用于关联和查询，创建索引提高查询性能
    id = Column(BigInteger, nullable=False, index=True)


# 账号使用记录模型 - 跟踪账号的使用情况
class AccountUsageRecordModel(Base):
    __tablename__ = "account_usage_records"  # 表名
    
    # 自增ID作为主键
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # 关联到AccountModel的id字段，创建索引
    account_id = Column(BigInteger, nullable=False, index=True)  # 账号ID
    
    # 账号邮箱，用于关联查询，创建索引
    email = Column(String, nullable=False, index=True)  # 账号邮箱
    
    # 使用者IP地址，可为空
    ip = Column(String, nullable=True)  # 使用者IP
    
    # 使用者的User-Agent信息，可为空
    user_agent = Column(Text, nullable=True)  # 使用者UA
    
    # 记录创建时间，不可为空
    created_at = Column(Text, nullable=False)  # 创建时间


def create_engine():
    """
    创建数据库引擎
    
    返回:
        SQLAlchemy异步引擎实例
        
    说明:
        - 使用配置文件中的数据库URL创建引擎
        - 对于SQLite数据库，设置check_same_thread=False以允许多线程访问
        - echo=False关闭SQL语句日志输出
    """
    # 直接使用配置文件中的数据库URL
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        future=True,
    )
    # info(f"数据库引擎创建成功: {DATABASE_URL}")
    return engine


@asynccontextmanager
async def get_session() -> AsyncSession:
    """
    创建数据库会话的异步上下文管理器
    
    用法:
        async with get_session() as session:
            # 使用session进行数据库操作
    
    返回:
        AsyncSession实例
        
    异常:
        捕获并记录数据库连接和操作异常，并确保资源正确释放
    """
    # 为每个请求创建新的引擎和会话，确保线程安全
    engine = create_engine()
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, future=True
    )

    session = async_session()
    try:
        # 执行简单查询以确保连接有效
        await session.execute(text("SELECT 1"))
        yield session
    except Exception as e:
        # 记录错误并尝试回滚事务
        error(f"数据库会话错误: {str(e)}")
        try:
            await session.rollback()
        except Exception as rollback_error:
            error(f"回滚过程中出错: {str(rollback_error)}")
        raise
    finally:
        # 无论成功与否，都确保关闭会话和释放引擎
        try:
            await session.close()
        except Exception as e:
            error(f"关闭会话时出错: {str(e)}")
        try:
            await engine.dispose()
        except Exception as e:
            error(f"释放引擎时出错: {str(e)}")


async def init_db():
    """
    初始化数据库表结构
    
    功能:
        - 根据定义的模型创建数据库表
        - 如果表已存在，不会重新创建
        
    异常:
        捕获并记录初始化过程中的错误
    """
    try:
        # 创建数据库引擎
        engine = create_engine()
        # 开始事务并创建表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        # 释放引擎资源
        await engine.dispose()
        info("数据库初始化成功")
    except Exception as e:
        error(f"数据库初始化失败: {str(e)}")
        raise
