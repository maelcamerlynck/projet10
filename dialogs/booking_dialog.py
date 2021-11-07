# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog
from .dateback_resolver_dialog import DatebackResolverDialog
from botbuilder.applicationinsights import ApplicationInsightsTelemetryClient
from botbuilder.integration.applicationinsights.aiohttp import (AiohttpTelemetryProcessor,bot_telemetry_middleware)
from config import DefaultConfig



class BookingDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None,telemetry_client: BotTelemetryClient = NullTelemetryClient()):
        super(BookingDialog, self).__init__(dialog_id or BookingDialog.__name__, telemetry_client)
        self.telemetry_client = telemetry_client
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.destination_step,
                self.origin_step,
                self.travel_date_step,
                # self.confirm_step,
                self.final_step,
            ],
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(DateResolverDialog(DateResolverDialog.__name__))
        self.add_dialog(DatebackResolverDialog(DatebackResolverDialog.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.destination_step,
                    self.origin_step,
                    self.travel_date_step,
                    self.travel_date_back_step,
                    self.money_step,
                    self.confirm_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__
        

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a destination city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        print('3')

        if booking_details.destination is None:
            message_text = "Where would you like to travel to?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If an origin city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        if booking_details.origin is None:
            message_text = "From what city will you be travelling?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
            print(booking_details.origin)
        return await step_context.next(booking_details.origin)

    async def travel_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a travel date has not been provided, prompt for one.
        This will use the DATE_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.origin = step_context.result
        if not booking_details.travel_date:
            return await step_context.begin_dialog(
                DateResolverDialog.__name__, booking_details.travel_date
            )
        return await step_context.next(booking_details.travel_date)

    async def travel_date_back_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If a travel date has not been provided, prompt for one.
        This will use the DATEBBACK_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.travel_date = step_context.result
        if not booking_details.travel_date_back:
            return await step_context.begin_dialog(
                DatebackResolverDialog.__name__, booking_details.travel_date_back
            )
        return await step_context.next(booking_details.travel_date_back)

   

    async def money_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If a price has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.travel_date_back = step_context.result
        if booking_details.money is None:
            message_text = "Which amount of money max would you like to spend on your ticket?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.money)  
    
    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        Confirm the information the user has provided.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.money = step_context.result
        message_text = (
            f"Please confirm, I have you traveling to: { booking_details.destination } from: "
            f"{ booking_details.origin } on: { booking_details.travel_date} returning on { booking_details.travel_date_back} for a maximum amount of { booking_details.money }."
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        #record details to send to azure insights
        details_insights = {}
        details_insights['destination'] = booking_details.destination
        details_insights['origin'] = booking_details.origin
        details_insights['departure_date'] = booking_details.travel_date
        details_insights['return_date'] = booking_details.travel_date_back
        details_insights['money'] = booking_details.money
        INSTRUMENTATION_KEY = DefaultConfig.APPINSIGHTS_INSTRUMENTATION_KEY
        #print(INSTRUMENTATION_KEY)
        TELEMETRY_CLIENT = ApplicationInsightsTelemetryClient(INSTRUMENTATION_KEY, telemetry_processor=AiohttpTelemetryProcessor(), client_queue_size=10)       
        if step_context.result:
            #tester si l'envoie se fait correctement vers Azure insight
            print('insights P10_FLIGHTBOOKINGBOT 1')
            TELEMETRY_CLIENT.track_trace('good', details_insights, 'details')
            #self.telemetry_client.track_trace('good', details_insights, 'details')
            TELEMETRY_CLIENT.flush()
            print('insights P10_FLIGHTBOOKINGBOT 2')
            return await step_context.end_dialog(booking_details)
        print('insights P10_FLIGHTBOOKINGBOT 3')
        TELEMETRY_CLIENT.track_trace('bad', details_insights, 'details')
        TELEMETRY_CLIENT.flush()
        print('insights P10_FLIGHTBOOKINGBOT 4')
        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
