import math

class BaseCalculator:
    """
    그린의 정리를 이용한 Geometry Properties 계산
    """
    @staticmethod
    def calculate_area(vertices, factor = 1.0):
        """면적 계산"""
        y = vertices["y"]
        z = vertices["z"]
        
        area = 0.0
        
        for i in range(len(y)-1):
            area += (y[i] * z[i+1] - y[i+1] * z[i]) * factor
        
        return area / 2.0
    
    @staticmethod
    def calculate_perimeter(vertices):
        """둘레 계산"""
        y = vertices["y"]
        z = vertices["z"]
        
        perimeter = 0.0
        
        for i in range(len(y)-1):
            dx = y[i+1] - y[i]
            dy = z[i+1] - z[i]
            perimeter += math.sqrt(dx*dx + dy*dy)
        
        return perimeter
    
    @staticmethod
    def calculate_centroid(vertices, factor = 1.0):
        """무게중심 계산"""
        y = vertices["y"]
        z = vertices["z"]
        
        area = BaseCalculator.calculate_area(vertices, factor)
        if area == 0:
            return (0, 0)
            
        cx, cy = 0.0, 0.0
        
        for i in range(len(y)-1):
            j = (i + 1) % len(y)
            common = y[i] * z[j] - z[i] * y[j]
            cx += (y[i] + y[j]) * common * factor
            cy += (z[i] + z[j]) * common * factor
        
        cx = cx / (6 * area)
        cy = cy / (6 * area)
        
        return (cx, cy)
    
    @staticmethod
    def calculate_moment_of_inertia(vertices, cy, cz, factor = 1.0):
        """관성 모멘트 계산"""
        y = vertices["y"].copy()
        z = vertices["z"].copy()
        
        for i in range(len(y)):
            y[i] = y[i] - cy
            z[i] = z[i] - cz
        
        Iyy, Izz, Iyz = 0.0, 0.0, 0.0
        
        for i in range(len(y)-1):
            j = (i + 1)
            yi, zi = y[i], z[i]
            yj, zj = y[j], z[j]
            
            # 관성 모멘트 계산 공식
            common = (yi * zj - yj * zi) / 12.0
            Iyy += common * (zi*zi + zi*zj + zj*zj) * factor
            Izz += common * (yi*yi + yi*yj + yj*yj) * factor
            Iyz += common * (yi*zj + 2*yi*zi + 2*yj*zj + yj*zi) * factor
        
        return {"Iyy": Iyy, "Izz": Izz, "Iyz": Iyz}
    
