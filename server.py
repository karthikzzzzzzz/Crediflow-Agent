from mcp.server.fastmcp import FastMCP
import uvicorn
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server

mcp = FastMCP("Risk-Agent")

@mcp.tool()
def analyze_bank_statement(transactions:int):
    """
    Analyzes a bank statement(transactions) to display the user is spending more or not
    
    Args:
        transactions of the account
    """
    if transactions <10000:
        return f"You are saving your money well and your expenses are less than {transactions}"
    else:
        return f"You are not saving your money well and your expenses are more than {transactions}"

@mcp.tool()
def check_credit_score(credit_score:int):
    """
    Checks the credit score is in the range or not
    
    Args:
        credit score of the user
    """
    if credit_score>500:
        return f"Credit score is ook which is {credit_score}"
    else:
        return f"Credit score is not ok which is {credit_score}"

@mcp.tool()
def analyze_gst_returns(gst:int):
    """
    Analyzes GST data to interpret the percentage of gst.

    Args:
        gst of the user

    """
    if gst<500:
        return f"The gst is less in percentage which is {gst}"
    else:
        return f"The gst is more in percentage which is {gst}"


@mcp.tool()
def human_assistance(query:str):
    """
    This tool will take the input from the person who is called as human in the loop
    """
    return f"Human is currently busy, so your query {query} will be answered in short time"

@mcp.tool()
def compute_risk_score(credit_score:int,transactions:int,gst:int):
    """
    Computes a final risk score based on credit score, bank analysis, and GST analysis.

    Args:
        Credit score,transactions, gst of the user
    """
    credit_score_norm = max(0, min((credit_score - 300) / 600, 1))  
    transactions_norm = min(transactions / 100, 1)                  
    gst_norm = min(gst / 100, 1)                                     
    w1, w2, w3 = 0.5, 0.2, 0.3  
    risk_score = (w1 * credit_score_norm + w2 * transactions_norm + w3 * gst_norm) * 100
    return round(risk_score,2)

    

@mcp.tool()
def generate_report(credit_score:int,transactions:int,gst:int):
    """
    Generates a underwriting summary based on all analysis components.

    Args:
        Credit score,transactions, gst of the user
       
    """
    risk_score=compute_risk_score(credit_score,transactions,gst)
    if risk_score >= 80:
        risk_level = "Low Risk"
        remark = "Applicant has strong financials and low risk of default."
    elif risk_score >= 60:
        risk_level = "Moderate Risk"
        remark = "Applicant has acceptable credit and financial behavior but some concerns remain."
    else:
        risk_level = "High Risk"
        remark = "Applicant has poor financial indicators and is at high risk of default."

    report = f"""
    Underwriting Summary Report
    -----------------------------
    Credit Score     : {credit_score}    
    Bank Transactions: {transactions} txns/month
    GST Compliance   : {gst}/100

    Calculated Risk Score: {risk_score}/100
    Risk Level           : {risk_level}

    Remarks: {remark}
        """.strip()

    return report   


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server
    
    starlette_app = create_starlette_app(mcp_server, debug=True)
    port = 9095
    print(f"Starting MCP server with SSE transport on port {port}...")
    print(f"SSE endpoint available at: http://localhost:{port}/sse")
    
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)