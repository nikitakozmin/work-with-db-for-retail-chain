from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class StoreClass(Base):
    __tablename__ = 'store_class'
    
    store_class_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    
    stores = relationship("Store", back_populates="store_class")
    product_prices = relationship("ProductPrice", back_populates="store_class")

class TradingBase(Base):
    __tablename__ = 'trading_base'
    
    trading_base_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    warehouse_products = relationship("WarehouseProduct", back_populates="trading_base")
    warehouse_priorities = relationship("WarehousePriority", back_populates="trading_base")

class Employee(Base):
    __tablename__ = 'employee'
    
    employee_id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    
    managed_stores = relationship("Store", back_populates="director")
    managed_departments = relationship("Department", back_populates="manager")

class Store(Base):
    __tablename__ = 'store'
    
    store_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    store_class_id = Column(Integer, ForeignKey('store_class.store_class_id'))
    director_id = Column(Integer, ForeignKey('employee.employee_id'))
    
    store_class = relationship("StoreClass", back_populates="stores")
    director = relationship("Employee", back_populates="managed_stores")
    departments = relationship("Department", back_populates="store")
    warehouse_priorities = relationship("WarehousePriority", back_populates="store")

class Department(Base):
    __tablename__ = 'department'
    
    department_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('store.store_id'))
    manager_id = Column(Integer, ForeignKey('employee.employee_id'))
    name = Column(String(100), nullable=False)
    
    store = relationship("Store", back_populates="departments")
    manager = relationship("Employee", back_populates="managed_departments")
    department_products = relationship("DepartmentProduct", back_populates="department")

class Product(Base):
    __tablename__ = 'product'
    
    article = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    sort = Column(String(50))
    
    department_products = relationship("DepartmentProduct", back_populates="product")
    warehouse_products = relationship("WarehouseProduct", back_populates="product")
    product_prices = relationship("ProductPrice", back_populates="product")
    warehouse_priorities = relationship("WarehousePriority", back_populates="product")

class DepartmentProduct(Base):
    __tablename__ = 'department_product'
    
    department_id = Column(Integer, ForeignKey('department.department_id'), primary_key=True)
    article = Column(Integer, ForeignKey('product.article'), primary_key=True)
    count = Column(Integer, default=0)
    
    department = relationship("Department", back_populates="department_products")
    product = relationship("Product", back_populates="department_products")

class WarehouseProduct(Base):
    __tablename__ = 'warehouse_product'
    
    trading_base_id = Column(Integer, ForeignKey('trading_base.trading_base_id'), primary_key=True)
    article = Column(Integer, ForeignKey('product.article'), primary_key=True)
    count = Column(Integer, default=0)
    price = Column(DECIMAL(10, 2), nullable=False)
    
    trading_base = relationship("TradingBase", back_populates="warehouse_products")
    product = relationship("Product", back_populates="warehouse_products")

class ProductPrice(Base):
    __tablename__ = 'product_price'
    
    store_class_id = Column(Integer, ForeignKey('store_class.store_class_id'), primary_key=True)
    article = Column(Integer, ForeignKey('product.article'), primary_key=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    
    store_class = relationship("StoreClass", back_populates="product_prices")
    product = relationship("Product", back_populates="product_prices")

class WarehousePriority(Base):
    __tablename__ = 'warehouse_priority'
    
    article = Column(Integer, ForeignKey('product.article'), primary_key=True)
    store_id = Column(Integer, ForeignKey('store.store_id'), primary_key=True)
    trading_base_id = Column(Integer, ForeignKey('trading_base.trading_base_id'), primary_key=True)
    priority = Column(Integer, default=5)
    
    product = relationship("Product", back_populates="warehouse_priorities")
    store = relationship("Store", back_populates="warehouse_priorities")
    trading_base = relationship("TradingBase", back_populates="warehouse_priorities")
