import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.ext import ConversationHandler
from weasyprint import HTML

EDUCATION_PROGRAM_OPTIONS = ["BTech"]
SEMESTER_OPTIONS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
EXAM_YEAR_OPTIONS = ["2019", "2020", "2021", "2022", "2023", "2024"]
BATCH_YEAR_OPTIONS = ["2019","2020","2021", "2022", "2023", "2024"]

SEMESTER_IN_LETTER_MAP = {"I": "1st",
                          "II": "2nd",
                          "III": "3rd",
                          "IV": "4th",
                          "V": "5th",
                          "VI": "6th",
                          "VII": "7th",
                          "VIII": "8th"
                          }

# State constants for conversation
EDUCATION_PROGRAM, REGISTRATION_NO, SEMESTER, EXAM_YEAR, BATCH_YEAR = range(5)


# Function to start the conversation
def start(update: Update, context: CallbackContext) -> int:
    reply_markup = ReplyKeyboardMarkup([[option] for option in EDUCATION_PROGRAM_OPTIONS], one_time_keyboard=True)
    update.message.reply_text("Welcome to the Result Bot! Please select your education program:",
                              reply_markup=reply_markup)
    return EDUCATION_PROGRAM


# Function to handle each step of the conversation
def education_program(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    # Process user input (validate if needed)
    context.user_data['education_program'] = user_input
    update.message.reply_text("Please enter your registration number:")
    return REGISTRATION_NO


def registration_no(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    # Process user input (validate if needed)
    context.user_data['registration_no'] = user_input
    reply_markup = ReplyKeyboardMarkup([[option] for option in SEMESTER_OPTIONS], one_time_keyboard=True)
    update.message.reply_text("Please select your semester:", reply_markup=reply_markup)
    return SEMESTER


def semester(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    # Process user input (validate if needed)
    context.user_data['semester'] = user_input
    update.message.reply_text("Please select the exam session year:",
                              reply_markup=ReplyKeyboardMarkup([[option] for option in EXAM_YEAR_OPTIONS],
                                                               one_time_keyboard=True))
    return EXAM_YEAR


def exam_year(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    # Process user input (validate if needed)
    context.user_data['exam_year'] = user_input
    update.message.reply_text("Please select the batch year:",
                              reply_markup=ReplyKeyboardMarkup([[option] for option in BATCH_YEAR_OPTIONS],
                                                               one_time_keyboard=True))
    return BATCH_YEAR


def batch_year(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Please Wait..., We are pulling your Result for the provided details")
    user_input = update.message.text
    # Process user input (validate if needed)
    context.user_data['batch_year'] = user_input
    # Process user inputs (validate and hit the URL)
    # Your logic to validate inputs and hit the URL goes here...
    SEMESTER_IN_LETTER = SEMESTER_IN_LETTER_MAP.get(context.user_data['semester'])

    BASE_URL = f"http://results.beup.ac.in/Results{context.user_data['education_program']}{SEMESTER_IN_LETTER}Sem{context.user_data['exam_year']}_B{context.user_data['batch_year']}Pub.aspx?Sem={context.user_data['semester']}&RegNo={context.user_data['registration_no']}"
    pdf_path = f"result_{context.user_data['registration_no']}_output.pdf"
    response_page = requests.get(BASE_URL)
    # For demonstration, let's assume a successful response
    if response_page.status_code == 200:
        HTML(string=response_page.content).write_pdf(pdf_path)
        # Return the PDF file
        update.message.reply_text("Result Found. Sending the PDF file...")
        context.bot.send_document(update.message.chat_id, document=open(pdf_path, 'rb'))
        # Check if the file exists
        if os.path.exists(pdf_path):
            # Delete the file
            os.remove(pdf_path)
            #print("File deleted successfully.")
    else:
        # Return an error message
        update.message.reply_text("Sorry, the provided inputs are not correct. Please try again.")

    # End conversation
    update.message.reply_text("Please type /start to check another result")
    return ConversationHandler.END


# Main function to start the bot
def main() -> None:
    # Set up the Telegram Bot
    updater = Updater("7062024356:AAGa6H5IttXInaqZp0S9k0EqVyd1-5kqcXU")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Create ConversationHandler with states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            EDUCATION_PROGRAM: [MessageHandler(Filters.text & ~Filters.command, education_program)],
            REGISTRATION_NO: [MessageHandler(Filters.text & ~Filters.command, registration_no)],
            SEMESTER: [MessageHandler(Filters.text & ~Filters.command, semester)],
            EXAM_YEAR: [MessageHandler(Filters.text & ~Filters.command, exam_year)],
            BATCH_YEAR: [MessageHandler(Filters.text & ~Filters.command, batch_year)]
        },
        fallbacks=[],
    )

    # Add ConversationHandler to dispatcher
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
