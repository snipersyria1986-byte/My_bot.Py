import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import time
from collections import defaultdict

# تكوين التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7674783654:AAEsfosyZs40Aklk8hzB5L6fWMuiNQXa73o"

# قاعدة البيانات للخدمات والأسعار
SERVICES = {
    "marketing": {
        "name": "📱 التسويق الإلكتروني",
        "services": {
            "m1": {"name": "إنشاء صفحات تواصل احترافية", "price": "50-100$", "duration": "3-5 أيام"},
            "m2": {"name": "تصميم لوغو احترافي", "price": "30-80$", "duration": "2-3 أيام"},
            "m3": {"name": "كتابة وتحرير مناشير", "price": "20-50$", "duration": "1-2 أيام"},
            "m4": {"name": "دراسة حالة العملاء", "price": "100-200$", "duration": "5-7 أيام"},
            "m5": {"name": "تقييم الصفحات وطرق التطوير", "price": "80-150$", "duration": "3-4 أيام"},
            "m6": {"name": "تصميم فيديوهات قصيرة", "price": "40-100$", "duration": "2-4 أيام"},
            "m7": {"name": "حملات إعلانية على السوشيال ميديا", "price": "200-500$", "duration": "شهري"},
            "m8": {"name": "تصميم بوتات رد تلقائي", "price": "150-300$", "duration": "5-10 أيام"},
            "m9": {"name": "دراسة المحتوى لزيادة التفاعل", "price": "120-250$", "duration": "4-6 أيام"},
            "m10": {"name": "استشارات دائمة بعد انتهاء العرض", "price": "50-100$", "duration": "شهري"}
        }
    },
    
    "security": {
        "name": "🔒 الأمن السيبراني", 
        "services": {
            "s1": {"name": "حماية المواقع من الاختراق", "price": "300-600$", "duration": "7-14 يوم"},
            "s2": {"name": "اختبار الاختراق (Penetration Testing)", "price": "400-800$", "duration": "10-15 يوم"},
            "s3": {"name": "مراقبة الشبكات 24/7", "price": "200-400$", "duration": "شهري"},
            "s4": {"name": "استشارات أمنية", "price": "100-250$", "duration": "حسب الطلب"},
            "s5": {"name": "تدريب موظفين على الأمن", "price": "150-300$", "duration": "3-5 أيام"}
        }
    },
    
    "design": {
        "name": "💻 تصميم مواقع ويب",
        "services": {
            "d1": {"name": "مواقع متجاوبة (Responsive)", "price": "200-500$", "duration": "7-14 يوم"},
            "d2": {"name": "متاجر إلكترونية", "price": "400-1000$", "duration": "14-30 يوم"},
            "d3": {"name": "مواقع شركات", "price": "300-700$", "duration": "10-20 يوم"},
            "d4": {"name": "تطبيقات ويب", "price": "500-1500$", "duration": "20-40 يوم"},
            "d5": {"name": "صيانة وتحديث المواقع", "price": "100-300$", "duration": "حسب الطلب"}
        }
    }
}

# قائمة الكلمات البذيئة (يمكن إضافة المزيد)
BAD_WORDS = [
    'كس', 'طيز', 'شرموطة', 'عاهر', 'زبالة', 'قحبة', 'منيوك', 'منيوكة', 'كلب', 'ابن الكلب',
    'خرا', 'عير', 'زق', 'فاجر', 'فاجرة', 'دعارة', 'زاني', 'زانية', 'فحل', 'فحلة',
    'قحاب', 'شراميط', 'أولاد الحرام', 'بنات الحرام', 'يلعن', 'يلعنه', 'يلعنك', 'سب',
    'اشتم', 'قحبه', 'شرموطه', 'زق', 'خرة', 'طيزه', 'طيزك'
]

# تخزين تحذيرات المستخدمين
user_warnings = defaultdict(int)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """القائمة الرئيسية"""
    try:
        # التحقق إذا كانت المحادثة مجموعة
        if update.message.chat.type in ['group', 'supergroup']:
            await update.message.reply_text(
                "👋 أنا بوت الخدمات! للتفاعل معي راسلني خاص"
            )
            return
            
        keyboard = [
            [InlineKeyboardButton("📱 التسويق الإلكتروني", callback_data="category_marketing")],
            [InlineKeyboardButton("🔒 الأمن السيبراني", callback_data="category_security")],
            [InlineKeyboardButton("💻 تصميم مواقع ويب", callback_data="category_design")],
            [InlineKeyboardButton("📞 التواصل المباشر", callback_data="contact")]
        ]
        
        await update.message.reply_text(
            "🚀 **مرحباً! اختر القسم الذي تريده:**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل في المجموعات فقط"""
    try:
        # التحقق إذا كانت المجموعة
        if update.message.chat.type not in ['group', 'supergroup']:
            return
            
        # تخطي الرسائل من البوت نفسه
        if update.message.from_user and update.message.from_user.is_bot:
            return
            
        user_id = update.message.from_user.id
        chat_id = update.message.chat.id
        message_text = update.message.text.lower() if update.message.text else ""
        
        # التحقق من الكلمات البذيئة
        found_bad_word = False
        for word in BAD_WORDS:
            if word in message_text:
                found_bad_word = True
                break
                
        if found_bad_word:
            # حذف الرسالة
            try:
                await update.message.delete()
                logger.info(f"Deleted message with bad word from user {user_id}")
            except Exception as delete_error:
                logger.error(f"Error deleting message: {delete_error}")
                await context.bot.send_message(chat_id, "❌ لا أستطيع حذف الرسالة. تأكد من أن لدي صلاحية حذف الرسائل.")
                return
            
            # إضافة تحذير للمستخدم
            user_warnings[user_id] += 1
            
            warning_msg = ""
            if user_warnings[user_id] == 1:
                warning_msg = f"⚠️ تحذير للمستخدم {update.message.from_user.first_name}! هذه المرة الأولى."
            elif user_warnings[user_id] == 2:
                warning_msg = f"⚠️ تحذير ثاني للمستخدم {update.message.from_user.first_name}! هذه المرة الثانية."
            else:
                # حذف المستخدم بعد 3 تحذيرات
                try:
                    await context.bot.ban_chat_member(chat_id, user_id)
                    warning_msg = f"🚫 تم حظر المستخدم {update.message.from_user.first_name} بسبب تكرار الإساءة."
                    user_warnings[user_id] = 0  # إعادة الضبط
                    logger.info(f"Banned user {user_id} for repeated bad words")
                except Exception as ban_error:
                    warning_msg = f"❌ لا يمكنني حظر المستخدم. تأكد من أن لدي الصلاحيات الكافية."
                    logger.error(f"Ban error: {ban_error}")
            
            await context.bot.send_message(chat_id, warning_msg)
                
    except Exception as e:
        logger.error(f"Error in group message handling: {e}")

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الضغط على الأزرار"""
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("category_"):
            category = data.split("_")[1]
            await show_services(query, category)
            
        elif data.startswith("service_"):
            parts = data.split("_")
            service_id = parts[1]
            category = parts[2]
            await show_service_details(query, service_id, category)
            
        elif data == "contact":
            await show_contact(query)
            
        elif data == "back":
            await start_from_query(query)
            
    except Exception as e:
        logger.error(f"Error in button click: {e}")
        try:
            await query.edit_message_text("❌ حدث خطأ ما. يرجى المحاولة مرة أخرى.")
        except:
            pass

async def start_from_query(query):
    """بدء البوت من استعلام (لزر الرجوع)"""
    try:
        keyboard = [
            [InlineKeyboardButton("📱 التسويق الإلكتروني", callback_data="category_marketing")],
            [InlineKeyboardButton("🔒 الأمن السيبراني", callback_data="category_security")],
            [InlineKeyboardButton("💻 تصميم مواقع ويب", callback_data="category_design")],
            [InlineKeyboardButton("📞 التواصل المباشر", callback_data="contact")]
        ]
        
        await query.edit_message_text(
            "🚀 **مرحباً! اختر القسم الذي تريده:**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in start from query: {e}")

async def show_services(query, category):
    """عرض خدمات القسم"""
    try:
        category_data = SERVICES.get(category)
        if not category_data:
            await query.edit_message_text("❌ القسم غير موجود.")
            return
        
        keyboard = []
        for service_id, service in category_data["services"].items():
            keyboard.append([InlineKeyboardButton(
                f"• {service['name']}", 
                callback_data=f"service_{service_id}_{category}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back")])
        
        await query.edit_message_text(
            f"📋 **{category_data['name']}**\n\n"
            "اختر الخدمة التي تريدها:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing services: {e}")
        await query.edit_message_text("❌ حدث خطأ ما. يرجى المحاولة مرة أخرى.")

async def show_service_details(query, service_id, category):
    """عرض تفاصيل الخدمة"""
    try:
        category_data = SERVICES.get(category)
        if not category_data or service_id not in category_data["services"]:
            await query.edit_message_text("❌ الخدمة غير موجودة.")
            return
        
        service = category_data["services"][service_id]
        
        message = (
            f"🔍 *{service['name']}*\n\n"
            f"💰 *السعر:* {service['price']}\n"
            f"⏰ *المدة:* {service['duration']}\n\n"
            f"📞 *للطلب أو الاستفسار:*\n"
            f"• Telegram: @developers_Ahmad\n"
            f"• WhatsApp: +963957248651\n\n"
            f"💬 تواصل معنا الآن لبدء المشروع!"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع للخدمات", callback_data=f"category_{category}")],
            [InlineKeyboardButton("📞 التواصل المباشر", callback_data="contact")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error showing service details: {e}")
        try:
            service = category_data["services"][service_id]
            message = (
                f"🔍 {service['name']}\n\n"
                f"💰 السعر: {service['price']}\n"
                f"⏰ المدة: {service['duration']}\n\n"
                f"📞 للطلب أو الاستفسار:\n"
                f"• Telegram: @developers_Ahmad\n"
                f"• WhatsApp: +963957248651\n\n"
                f"💬 تواصل معنا الآن لبدء المشروع!"
            )
            await query.edit_message_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=None
            )
        except:
            await query.edit_message_text("❌ حدث خطأ ما. يرجى المحاولة مرة أخرى.")

async def show_contact(query):
    """عرض معلومات التواصل - الإصلاح هنا"""
    try:
        message = (
            "📞 *التواصل المباشر:*\n\n"
            "👤 *المسؤول:* أحمد أبو يوسف\n"
            "📱 *Telegram:* @developers_Ahmad\n"
            "📞 *WhatsApp:* +963957248651\n"
            "🕒 *الوقت:* 24/7\n\n"
            "💬 *تواصل معنا الآن للبدء بمشروعك!*"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back")]
        ]
        
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error showing contact: {e}")
        # محاولة بدون ماركداون في حالة الخطأ
        try:
            message = (
                "📞 التواصل المباشر:\n\n"
                "👤 المسؤول: أحمد أبو يوسف\n"
                "📱 Telegram: @developers_Ahmad\n"
                "📞 WhatsApp: +963957248651\n"
                "🕒 الوقت: 24/7\n\n"
                "💬 تواصل معنا الآن للبدء بمشروعك!"
            )
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=None
            )
        except Exception as e2:
            logger.error(f"Second error in contact: {e2}")
            await query.edit_message_text("❌ حدث خطأ ما. يرجى المحاولة مرة أخرى.")

async def reset_warnings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إعادة ضبط تحذيرات المستخدم (للمشرفين)"""
    try:
        if update.message.chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ هذا الأمر للمجموعات فقط!")
            return
            
        # التحقق إذا كان المستخدم مشرف
        user = await update.message.chat.get_member(update.message.from_user.id)
        if user.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ هذا الأمر للمشرفين فقط!")
            return
            
        if context.args:
            user_id = int(context.args[0])
            user_warnings[user_id] = 0
            await update.message.reply_text(f"✅ تم إعادة ضبط تحذيرات المستخدم {user_id}.")
        else:
            await update.message.reply_text("⚠️ يرجى تحديد ID المستخدم: /resetwarnings <user_id>")
            
    except Exception as e:
        logger.error(f"Error in reset_warnings: {e}")
        await update.message.reply_text("❌ حدث خطأ في الأمر.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام"""
    logger.error(f"حدث خطأ: {context.error}", exc_info=context.error)

def main():
    """تشغيل البوت"""
    try:
        application = Application.builder()\
            .token(BOT_TOKEN)\
            .read_timeout(30)\
            .write_timeout(30)\
            .connect_timeout(30)\
            .pool_timeout(30)\
            .build()
        
        # إضافة handlers مع الأولوية الصحيحة
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("resetwarnings", reset_warnings))
        application.add_handler(CallbackQueryHandler(handle_button_click))
        
        # معالجة رسائل المجموعات فقط (بأولوية منخفضة)
        group_handler = MessageHandler(
            filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND,
            handle_group_message
        )
        application.add_handler(group_handler)
        
        application.add_error_handler(error_handler)
        
        logger.info("✅ البوت يعمل بنظام القوائم المتداخلة وإدارة المجموعات...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.error(f"فشل تشغيل البوت: {e}")

if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
            print(f"Bot crashed, restarting in 5 seconds...")
            time.sleep(5)