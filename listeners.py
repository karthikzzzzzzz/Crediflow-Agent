import asyncio
from Data_acquistion_agent.kafka.listener import main as data_acquisition_listener
from Document_verification_agent.kafka.listener import main as document_verification_listener
from Eligibility_check_agent.kafka.listener import main as eligibility_check_listener
from Report_generation_agent.kafka.listener import main as report_generation_listener
from Screening_ops_maker_agent.kafka.listener import main as screening_ops_listener
from Back_office_agent.kafka.listener import main as back_office_listener

async def main():
    await asyncio.gather(
        data_acquisition_listener(),
        document_verification_listener(),
        eligibility_check_listener(),
        report_generation_listener(),
        screening_ops_listener(),
        back_office_listener()
    )

if __name__ == "__main__":
    asyncio.run(main())
