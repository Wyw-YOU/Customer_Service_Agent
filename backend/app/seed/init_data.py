"""
Seed data initialization script.
Generates mock users, products, orders, and knowledge documents for MVP development.
"""
import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "..")

from sqlalchemy import text

from app.config.database import async_session_factory, engine
from app.config.settings import settings
from app.models import Base
from app.models.aftersale import ApprovalTask, Refund
from app.models.agent import AgentRun, AgentStep, ToolLog
from app.models.conversation import Conversation, ConversationMessage
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.models.order import Logistics, Order, OrderItem
from app.models.product import Product, ProductSpec, ProductTag
from app.models.user import User, UserPreference

# ── Seed data ──────────────────────────────────────────────────────────────

PHONE_DATA = [
    {"name": "小米14 Pro", "brand": "Xiaomi", "category": "phone", "price": 4999,
     "cpu": "Snapdragon 8 Gen 3", "gpu": "Adreno 750", "screen": "6.73英寸 2K AMOLED",
     "camera": "徕卡光学 5000万像素", "battery": "4880mAh", "weight": "223g", "os": "HyperOS"},
    {"name": "iPhone 16 Pro", "brand": "Apple", "category": "phone", "price": 7999,
     "cpu": "A18 Pro", "gpu": "Apple 6-core", "screen": "6.3英寸 Super Retina XDR",
     "camera": "4800万像素 Fusion", "battery": "3571mAh", "weight": "199g", "os": "iOS 18"},
    {"name": "OPPO Find X8 Pro", "brand": "OPPO", "category": "phone", "price": 5299,
     "cpu": "Dimensity 9400", "gpu": "Immortalis-G925", "screen": "6.78英寸 1.5K AMOLED",
     "camera": "哈苏影像 5000万像素", "battery": "5910mAh", "weight": "215g", "os": "ColorOS 15"},
    {"name": "vivo X200 Pro", "brand": "vivo", "category": "phone", "price": 5299,
     "cpu": "Dimensity 9400", "gpu": "Immortalis-G925", "screen": "6.78英寸 1.5K AMOLED",
     "camera": "蔡司影像 200MP长焦", "battery": "6000mAh", "weight": "223g", "os": "OriginOS 5"},
    {"name": "华为 Mate 70 Pro", "brand": "Huawei", "category": "phone", "price": 6499,
     "cpu": "Kirin 9100", "gpu": "Maleoon 920", "screen": "6.82英寸 1.5K OLED",
     "camera": "XMAGE 5000万像素", "battery": "5500mAh", "weight": "221g", "os": "HarmonyOS NEXT"},
    {"name": "三星 Galaxy S25 Ultra", "brand": "Samsung", "category": "phone", "price": 9699,
     "cpu": "Snapdragon 8 Gen 4", "gpu": "Adreno 760", "screen": "6.9英寸 2K Dynamic AMOLED",
     "camera": "200MP 主摄", "battery": "5000mAh", "weight": "218g", "os": "One UI 7"},
    {"name": "一加 13", "brand": "OnePlus", "category": "phone", "price": 4499,
     "cpu": "Snapdragon 8 Gen 3", "gpu": "Adreno 750", "screen": "6.82英寸 2K AMOLED",
     "camera": "哈苏影像 5000万像素", "battery": "6000mAh", "weight": "220g", "os": "ColorOS"},
    {"name": "荣耀 Magic7 Pro", "brand": "Honor", "category": "phone", "price": 5299,
     "cpu": "Snapdragon 8 Gen 3", "gpu": "Adreno 750", "screen": "6.8英寸 1.5K OLED",
     "camera": "5000万像素 鹰眼相机", "battery": "5600mAh", "weight": "219g", "os": "MagicOS 9"},
    {"name": "红米 K80 Pro", "brand": "Redmi", "category": "phone", "price": 2999,
     "cpu": "Snapdragon 8 Gen 3", "gpu": "Adreno 750", "screen": "6.67英寸 2K AMOLED",
     "camera": "5000万像素", "battery": "6000mAh", "weight": "208g", "os": "HyperOS"},
    {"name": "真我 GT7 Pro", "brand": "realme", "category": "phone", "price": 3299,
     "cpu": "Snapdragon 8 Gen 3", "gpu": "Adreno 750", "screen": "6.78英寸 1.5K AMOLED",
     "camera": "5000万像素 索尼IMX890", "battery": "5800mAh", "weight": "205g", "os": "realme UI 6"},
    {"name": "iPhone 16", "brand": "Apple", "category": "phone", "price": 5999,
     "cpu": "A18", "gpu": "Apple 5-core", "screen": "6.1英寸 Super Retina XDR",
     "camera": "4800万像素", "battery": "3561mAh", "weight": "170g", "os": "iOS 18"},
    {"name": "小米15", "brand": "Xiaomi", "category": "phone", "price": 3999,
     "cpu": "Snapdragon 8 Gen 4", "gpu": "Adreno 760", "screen": "6.36英寸 1.5K AMOLED",
     "camera": "徕卡光学 5000万像素", "battery": "5400mAh", "weight": "191g", "os": "HyperOS"},
    {"name": "iQOO 13", "brand": "iQOO", "category": "phone", "price": 3999,
     "cpu": "Snapdragon 8 Gen 3", "gpu": "Adreno 750", "screen": "6.82英寸 2K AMOLED",
     "camera": "5000万像素", "battery": "6000mAh", "weight": "210g", "os": "OriginOS"},
    {"name": "努比亚 Z70 Ultra", "brand": "Nubia", "category": "phone", "price": 4499,
     "cpu": "Snapdragon 8 Gen 3", "gpu": "Adreno 750", "screen": "6.85英寸 1.5K AMOLED",
     "camera": "6400万像素", "battery": "6000mAh", "weight": "218g", "os": "MyOS"},
]

LAPTOP_DATA = [
    {"name": "MacBook Air M3", "brand": "Apple", "category": "laptop", "price": 8999,
     "cpu": "Apple M3", "gpu": "Apple 10-core", "screen": "13.6英寸 Liquid Retina",
     "camera": "1080p FaceTime", "battery": "18小时", "weight": "1.24kg", "os": "macOS"},
    {"name": "MacBook Pro 14 M3 Pro", "brand": "Apple", "category": "laptop", "price": 14999,
     "cpu": "Apple M3 Pro", "gpu": "Apple 18-core", "screen": "14.2英寸 Liquid Retina XDR",
     "camera": "1080p FaceTime", "battery": "17小时", "weight": "1.55kg", "os": "macOS"},
    {"name": "ThinkPad X1 Carbon Gen 12", "brand": "Lenovo", "category": "laptop", "price": 10999,
     "cpu": "Intel Core Ultra 7 155H", "gpu": "Intel Arc", "screen": "14英寸 2.8K OLED",
     "camera": "1080p IR", "battery": "15小时", "weight": "1.09kg", "os": "Windows 11"},
    {"name": "华为 MateBook X Pro 2025", "brand": "Huawei", "category": "laptop", "price": 9999,
     "cpu": "Intel Core Ultra 9 185H", "gpu": "Intel Arc", "screen": "14.2英寸 3.1K OLED",
     "camera": "1080p", "battery": "14小时", "weight": "980g", "os": "Windows 11"},
    {"name": "联想 YOGA Pro 14s", "brand": "Lenovo", "category": "laptop", "price": 7999,
     "cpu": "Intel Core Ultra 7 155H", "gpu": "Intel Arc", "screen": "14.5英寸 3K IPS",
     "camera": "1080p IR", "battery": "12小时", "weight": "1.29kg", "os": "Windows 11"},
    {"name": "华硕 灵耀14 2025", "brand": "ASUS", "category": "laptop", "price": 6999,
     "cpu": "Intel Core Ultra 7 155H", "gpu": "Intel Arc", "screen": "14英寸 2.8K OLED",
     "camera": "1080p", "battery": "15小时", "weight": "1.19kg", "os": "Windows 11"},
    {"name": "小米笔记本 Pro 16", "brand": "Xiaomi", "category": "laptop", "price": 5999,
     "cpu": "Intel Core i7-14650HX", "gpu": "NVIDIA RTX 4050", "screen": "16英寸 2.5K IPS",
     "camera": "1080p", "battery": "10小时", "weight": "1.88kg", "os": "Windows 11"},
    {"name": "戴尔 XPS 14", "brand": "Dell", "category": "laptop", "price": 9999,
     "cpu": "Intel Core Ultra 7 155H", "gpu": "NVIDIA RTX 4050", "screen": "14.5英寸 3.2K OLED",
     "camera": "1080p", "battery": "13小时", "weight": "1.43kg", "os": "Windows 11"},
]

WEARABLE_DATA = [
    {"name": "Apple Watch Series 10", "brand": "Apple", "category": "wearable", "price": 2999,
     "cpu": "S10 SiP", "gpu": None, "screen": "1.96英寸 LTPO OLED",
     "camera": None, "battery": "36小时", "weight": "35g", "os": "watchOS 11"},
    {"name": "华为 Watch GT 5 Pro", "brand": "Huawei", "category": "wearable", "price": 2488,
     "cpu": "麒麟 A1", "gpu": None, "screen": "1.43英寸 AMOLED",
     "camera": None, "battery": "14天", "weight": "48g", "os": "HarmonyOS"},
    {"name": "小米 Watch S4", "brand": "Xiaomi", "category": "wearable", "price": 999,
     "cpu": "BES2800", "gpu": None, "screen": "1.43英寸 AMOLED",
     "camera": None, "battery": "15天", "weight": "44g", "os": "HyperOS"},
    {"name": "三星 Galaxy Watch 7", "brand": "Samsung", "category": "wearable", "price": 1999,
     "cpu": "Exynos W1000", "gpu": None, "screen": "1.5英寸 Super AMOLED",
     "camera": None, "battery": "40小时", "weight": "33g", "os": "Wear OS 5"},
    {"name": "OPPO Watch 4 Pro", "brand": "OPPO", "category": "wearable", "price": 2299,
     "cpu": "Snapdragon W5 Gen 2", "gpu": None, "screen": "1.91英寸 AMOLED",
     "camera": None, "battery": "5天", "weight": "50g", "os": "ColorOS Watch"},
]

AUDIO_DATA = [
    {"name": "AirPods Pro 3", "brand": "Apple", "category": "audio", "price": 1799,
     "cpu": "H3", "gpu": None, "screen": None,
     "camera": None, "battery": "6小时+30小时", "weight": "5.3g", "os": None},
    {"name": "华为 FreeBuds 6 Pro", "brand": "Huawei", "category": "audio", "price": 1199,
     "cpu": "麒麟A3", "gpu": None, "screen": None,
     "camera": None, "battery": "8小时+36小时", "weight": "5.1g", "os": None},
    {"name": "小米 Buds 5 Pro", "brand": "Xiaomi", "category": "audio", "price": 699,
     "cpu": "BES2800", "gpu": None, "screen": None,
     "camera": None, "battery": "7小时+35小时", "weight": "4.9g", "os": None},
    {"name": "索尼 WH-1000XM6", "brand": "Sony", "category": "audio", "price": 2999,
     "cpu": "QN3", "gpu": None, "screen": None,
     "camera": None, "battery": "40小时", "weight": "250g", "os": None},
    {"name": "三星 Galaxy Buds3 Pro", "brand": "Samsung", "category": "audio", "price": 1299,
     "cpu": "BES2700", "gpu": None, "screen": None,
     "camera": None, "battery": "6小时+26小时", "weight": "5.4g", "os": None},
]

TABLET_DATA = [
    {"name": "iPad Air M3", "brand": "Apple", "category": "tablet", "price": 4799,
     "cpu": "Apple M3", "gpu": "Apple 9-core", "screen": "11英寸 Liquid Retina",
     "camera": "12MP 广角", "battery": "10小时", "weight": "462g", "os": "iPadOS 18"},
    {"name": "华为 MatePad Pro 14.2", "brand": "Huawei", "category": "tablet", "price": 4999,
     "cpu": "麒麟 9100", "gpu": "Maleoon 920", "screen": "14.2英寸 2.8K OLED",
     "camera": "13MP", "battery": "12小时", "weight": "580g", "os": "HarmonyOS"},
    {"name": "小米平板 7 Pro", "brand": "Xiaomi", "category": "tablet", "price": 2999,
     "cpu": "Snapdragon 8 Gen 3", "gpu": "Adreno 750", "screen": "12.4英寸 3K IPS",
     "camera": "50MP", "battery": "10000mAh", "weight": "570g", "os": "HyperOS"},
    {"name": "OPPO Pad 4 Pro", "brand": "OPPO", "category": "tablet", "price": 3299,
     "cpu": "Dimensity 9300", "gpu": "Immortalis-G720", "screen": "12.1英寸 3K IPS",
     "camera": "13MP", "battery": "9500mAh", "weight": "538g", "os": "ColorOS"},
]

ALL_PRODUCTS = PHONE_DATA + LAPTOP_DATA + WEARABLE_DATA + AUDIO_DATA + TABLET_DATA

USERS = [
    {"username": "admin", "password": "admin123", "email": "admin@mall.com", "role": "ADMIN"},
    {"username": "cs_agent", "password": "cs123", "email": "cs@mall.com", "role": "CUSTOMER_SERVICE"},
    {"username": "zhangsan", "password": "user123", "email": "zhangsan@mail.com", "role": "USER", "phone": "13800001001"},
    {"username": "lisi", "password": "user123", "email": "lisi@mail.com", "role": "USER", "phone": "13800001002"},
    {"username": "wangwu", "password": "user123", "email": "wangwu@mail.com", "role": "USER", "phone": "13800001003"},
    {"username": "zhaoliu", "password": "user123", "email": "zhaoliu@mail.com", "role": "USER", "phone": "13800001004"},
    {"username": "sunqi", "password": "user123", "email": "sunqi@mail.com", "role": "USER", "phone": "13800001005"},
]

ORDER_STATUSES = ["CREATED", "PAID", "SHIPPING", "DELIVERED", "CANCELLED"]
LOGISTICS_COMPANIES = ["顺丰速运", "京东物流", "中通快递", "圆通速递", "韵达快递"]
LOGISTICS_LOCATIONS = ["北京分拣中心", "上海中转站", "广州集散中心", "深圳配送站", "成都仓库"]

KNOWLEDGE_DOCUMENTS = [
    {
        "name": "数码商城退换货政策", "type": "POLICY",
        "content": """## 退换货政策

1. 7天无理由退货：自签收之日起7天内，商品完好可申请退货。
2. 15天质量问题换货：自签收之日起15天内，出现质量问题的商品可以换货。
3. 手机/平板等激活后不支持无理由退货。
4. 配件类商品一经拆封不支持退货。

## 退款流程

1. 提交退款申请
2. 客服审核（1-3个工作日）
3. 审核通过后退款（3-7个工作日到账）
4. 退款金额退回原支付方式"""
    },
    {
        "name": "手机选购FAQ", "type": "FAQ",
        "content": """## 常见手机选购问题

Q: 学生党预算3000元左右买什么手机？
A: 推荐红米K80 Pro、真我GT7 Pro、iQOO 13，性价比高，性能和拍照都够用。

Q: 拍照最好的手机是什么？
A: 当前拍照顶级的有：vivo X200 Pro（蔡司长焦）、小米14 Ultra（徕卡1英寸）、iPhone 16 Pro（视频录制）、华为Mate 70 Pro（XMAGE）。

Q: 游戏手机怎么选？
A: 重点关注散热、处理器和刷新率。iQOO 13、红米K80 Pro、一加13都非常适合游戏。

Q: 手机快充重要吗？
A: 如果你经常出门，续航和快充很重要。小米14 Pro支持120W快充，OPPO Find X8 Pro支持100W快充。"""
    },
    {
        "name": "笔记本选购指南", "type": "PRODUCT",
        "content": """## 笔记本选购指南

### 轻薄办公本
- MacBook Air M3：适合日常办公、学生使用，续航出色
- 华为MateBook X Pro：Windows轻薄本旗舰，屏幕素质好
- ThinkPad X1 Carbon：商务人士首选，键盘手感优秀

### 性能本
- MacBook Pro 14/16：创意工作者首选
- 小米笔记本Pro 16：性价比高，适合学生和入门创作
- 戴尔XPS 14：轻薄与性能兼顾

### 选购要点
1. 先确定用途（办公/编程/设计/游戏）
2. 关注屏幕素质（分辨率、色域）
3. 电池续航（轻薄本>8小时，性能本>5小时）
4. 接口数量和类型"""
    },
]


def generate_orders(user_ids: list[int], product_ids: list[int], count: int = 200) -> list[dict]:
    orders = []
    for i in range(count):
        user_id = random.choice(user_ids)
        status = random.choice(ORDER_STATUSES)
        item_count = random.randint(1, 3)
        items = []
        total = 0.0
        for _ in range(item_count):
            pid = random.choice(product_ids)
            product = next(p for p in ALL_PRODUCTS if p.get("_id") == pid)
            qty = random.randint(1, 2)
            price = product["price"]
            total += price * qty
            items.append({"product_id": pid, "quantity": qty, "price": price})
        order_no = f"ORD{datetime.now(timezone.utc).strftime('%Y%m%d')}{i+1:06d}"
        created = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
        orders.append({
            "user_id": user_id, "order_no": order_no, "status": status,
            "payment_status": "PAID" if status != "CREATED" else "PENDING",
            "total_amount": round(total, 2), "items": items, "created_at": created,
        })
    return orders


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    import bcrypt

    pwd_hasher = bcrypt

    async with async_session_factory() as session:
        # ── Users ──
        user_objs = []
        for u in USERS:
            user = User(
                username=u["username"],
                email=u.get("email"),
                phone=u.get("phone"),
                hashed_password=pwd_hasher.hashpw(u["password"].encode(), bcrypt.gensalt()).decode(),
                role=u["role"],
            )
            session.add(user)
            user_objs.append(user)
        await session.flush()
        user_ids = [u.id for u in user_objs]

        # ── Products ──
        product_objs = []
        for i, p in enumerate(ALL_PRODUCTS):
            product = Product(
                name=p["name"], brand=p["brand"], category=p["category"],
                price=p["price"], stock=random.randint(50, 500),
                status="ACTIVE",
                description=f"{p['brand']} {p['name']}，搭载{p.get('cpu', '高性能处理器')}",
            )
            session.add(product)
            product_objs.append(product)
        await session.flush()

        for i, (p, po) in enumerate(zip(ALL_PRODUCTS, product_objs)):
            p["_id"] = po.id
            spec = ProductSpec(
                product_id=po.id, cpu=p.get("cpu"), gpu=p.get("gpu"),
                screen=p.get("screen"), camera=p.get("camera"),
                battery=p.get("battery"), weight=p.get("weight"), os=p.get("os"),
            )
            session.add(spec)
            # Tags
            for tag in [p["brand"], p["category"]]:
                session.add(ProductTag(product_id=po.id, tag=tag))
        await session.flush()
        product_ids = [p.id for p in product_objs]

        # ── Orders ──
        orders_data = generate_orders(user_ids[:5], product_ids, 200)  # Only for normal users
        for od in orders_data:
            order = Order(
                user_id=od["user_id"], order_no=od["order_no"],
                status=od["status"], payment_status=od["payment_status"],
                total_amount=od["total_amount"],
            )
            session.add(order)
            await session.flush()
            for item in od["items"]:
                session.add(OrderItem(
                    order_id=order.id, product_id=item["product_id"],
                    quantity=item["quantity"], price=item["price"],
                ))
            # Logistics for SHIPPING/DELIVERED orders
            if od["status"] in ("SHIPPING", "DELIVERED"):
                company = random.choice(LOGISTICS_COMPANIES)
                session.add(Logistics(
                    order_id=order.id, company=company,
                    tracking_no=f"SF{random.randint(100000000, 999999999)}",
                    status="DELIVERED" if od["status"] == "DELIVERED" else "IN_TRANSIT",
                    location=random.choice(LOGISTICS_LOCATIONS),
                ))
        await session.flush()

        # ── Knowledge Documents ──
        for kd in KNOWLEDGE_DOCUMENTS:
            doc = KnowledgeDocument(
                name=kd["name"], type=kd["type"], version="v1.0", status="INDEXED",
            )
            session.add(doc)
            await session.flush()
            # Split content into chunks
            paragraphs = [p.strip() for p in kd["content"].split("\n\n") if p.strip()]
            for ci, para in enumerate(paragraphs):
                session.add(KnowledgeChunk(
                    document_id=doc.id,
                    chunk_id=f"{doc.id}_chunk_{ci}",
                    content=para,
                    meta={"source": kd["name"], "type": kd["type"]},
                ))
        await session.flush()

        # ── Conversations (sample) ──
        sample_convos = [
            Conversation(user_id=user_ids[2], title="手机推荐咨询"),
            Conversation(user_id=user_ids[3], title="订单查询"),
            Conversation(user_id=user_ids[2], title="售后申请"),
        ]
        for conv in sample_convos:
            session.add(conv)
        await session.flush()

        # Messages for first conversation
        messages = [
            ConversationMessage(conversation_id=sample_convos[0].id, role="user",
                              content="预算5000左右，喜欢拍照，有什么手机推荐？"),
            ConversationMessage(conversation_id=sample_convos[0].id, role="assistant",
                              content="根据您的需求，推荐以下三款拍照手机：小米14 Pro、vivo X200 Pro、OPPO Find X8 Pro。",
                              sources='["手机选购FAQ", "手机参数表"]'),
        ]
        for msg in messages:
            session.add(msg)

        # ── Sample Agent Runs ──
        run = AgentRun(
            conversation_id=sample_convos[0].id, query="预算5000左右拍照手机推荐",
            intent="PRODUCT_RECOMMEND", status="COMPLETED", latency_ms=2300, confidence=0.92,
        )
        session.add(run)
        await session.flush()

        steps = [
            AgentStep(run_id=run.id, node_name="intent_router", input_data={"query": "预算5000左右拍照手机推荐"},
                     output_data={"intent": "PRODUCT_RECOMMEND", "confidence": 0.92}, duration_ms=400),
            AgentStep(run_id=run.id, node_name="query_analyzer", input_data={"query": "预算5000左右拍照手机推荐"},
                     output_data={"category": "phone", "budget": 5000, "scenario": ["photo"]}, duration_ms=350),
            AgentStep(run_id=run.id, node_name="product_search", input_data={"category": "phone", "max_price": 5000},
                     output_data={"products_found": 8}, duration_ms=550),
            AgentStep(run_id=run.id, node_name="rag_retrieval", input_data={"query": "拍照手机"},
                     output_data={"chunks_retrieved": 5}, duration_ms=300),
            AgentStep(run_id=run.id, node_name="response_generator", input_data={"products": 3, "context": 5},
                     output_data={"response": "根据您的需求..."}, duration_ms=700),
        ]
        for step in steps:
            session.add(step)

        tool_log = ToolLog(
            run_id=run.id, tool_name="search_products",
            input_data={"keyword": "拍照手机", "budget": 5000, "category": "phone"},
            output_data={"products": [{"name": "小米14 Pro", "price": 4999}]},
            status="success", latency_ms=550,
        )
        session.add(tool_log)

        # ── Sample Refund + Approval ──
        refund = Refund(
            order_id=1, user_id=user_ids[2],
            reason="商品屏幕有亮点，影响使用体验",
            amount=ALL_PRODUCTS[0]["price"], status="PENDING_REVIEW",
        )
        session.add(refund)
        await session.flush()

        approval = ApprovalTask(
            type="REFUND", target_id=refund.id,
            risk_level="HIGH", status="PENDING",
        )
        session.add(approval)

        await session.commit()
        print(f"Seed data created successfully!")
        print(f"  Users: {len(user_objs)}")
        print(f"  Products: {len(product_objs)}")
        print(f"  Orders: {len(orders_data)}")
        print(f"  Knowledge docs: {len(KNOWLEDGE_DOCUMENTS)}")


if __name__ == "__main__":
    asyncio.run(seed())
