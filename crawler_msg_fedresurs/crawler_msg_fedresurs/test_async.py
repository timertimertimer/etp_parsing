# import asyncio
#
# async def nested():
#     return 42
#
# async def main():
#     # Schedule nested() to run soon concurrently
#     # with "main()".
#     await nested()
#
#
#     # "task" can now be used to cancel "nested()", or
#     # can simply be awaited to wait until it is complete:
#
#
# d = asyncio.run(main())
# print(d)
# from crawler_msg_fedresurs.utils.msg_types import msg_types as mt
#
#
# # for v in msg_types.values():
# #     for i in v:
# #         print(i)
# def return_msg_types_set():
#     new_set = set([y for x in list(mt.values()) for y in x])
#     return new_set

lst = [b'ASP.NET_SessionId=3lohrgor1h0aah3hcp1nfqoe; path=/; HttpOnly; SameSite=Lax', b'Messages=MessageNumber=&MessageType=TradeResult&MessageTypeText=%d0%a1%d0%be%d0%be%d0%b1%d1%89%d0%b5%d0%bd%d0%b8%d0%b5+%d0%be+%d1%80%d0%b5%d0%b7%d1%83%d0%bb%d1%8c%d1%82%d0%b0%d1%82%d0%b0%d1%85+%d1%82%d0%be%d1%80%d0%b3%d0%be%d0%b2&DateEndValue=09.01.2017+0%3a00%3a00&DateBeginValue=09.01.2017+0%3a00%3a00&PageNumber=2&DebtorText=&DebtorId=&DebtorType=&PublisherType=&PublisherId=&PublisherText=&IdRegion=&IdCourtDecisionType=&WithAu=False&WithViolation=False; path=/']
first = lst[0].decode('utf-8').split(';', maxsplit=1)[0] + ';'
second = lst[1].decode('utf-8').split(';', maxsplit=1)[0]

print(first + second)