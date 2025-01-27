links = set()

with open('/home/svdior/parse_etp/crawler_msg_fedresurs/links.txt', 'r') as f:
    lines = f.readlines()
    for l in lines:
        if len(l) > 10:
            links.add(l.rstrip())
for i,l in enumerate(links):
    print(f'{i}::{l}')

# Experimental code/ work only in spider file
#     async def serp_of_msg(self, response, p_headers, p_data, only_cookie, msg_type, current_page_arg):
#         # print(f'This is cookie received from cbcwargs {only_cookie}\n{p_headers}')
#         combo = ComboMsg(response_=response)
#         # msg_links_parse = list()
#         # pagination_lst - list with page number available on the serp page
#         # pagination_lst = combo.minfo.count_visible_pagination
#         # links to msg page
#         links = combo.minfo.link_to_msg_page()
#         if isinstance(links, list):
#             if len(links) > 0:
#                 logger.info(f'Count LINKS = {len(links)}')
#                 for link in links:
#                     link = self.return_link_for_msg_page(combo, link)
#                     with open('links.txt', 'a') as f:
#                         f.write(link)
#                         f.write('\n')
#                     headers_msg_page[':path'] = '/' + link.split('/')[-1]
#                     headers_msg_page['cookie'] = re.sub(r'\s+', ' ', combo.mpage.insert_extra_cookies(only_cookie))
#                     headers_msg_page['referer'] = response.url
#                     yield SplashRequest(link, callback=self.parse_msg_page,
#                                         # cookies=cookie_parser(headers_msg_page['cookie']),
#                                         splash_headers=headers_msg_page,
#                                         endpoint='execute',
#                                         cache_args=['lua_source'], args={'lua_source': script_lua_category},
#                                         slot_policy=SlotPolicy.PER_DOMAIN,
#                                         dont_filter=False,
#                                         errback=self.errback_httpbin,
#                                         cb_kwargs={'attemp': 0, 'link': link, 'msg_type': msg_type},
#                                         encoding='utf-8')
#         # check pagination
#         current_page = combo.minfo.get_current_page
#         if current_page_arg != current_page:
#             logger.critical(f'{p_data}')
#         import time
#         if current_page == 2:
#             time.sleep(1)
#             file_name = f'2_response_{return_parse_date()}.txt'.replace(':', '_').replace(' ', '_')
#             with open(file_name, 'w') as f:
#                 time.sleep(1)
#                 f.write(response.text)
#         if current_page == 1:
#             time.sleep(1)
#             file_name = f'1_response_{return_parse_date()}.txt'.replace(':', '_').replace(' ', '_')
#             with open(file_name, 'w') as f:
#                 time.sleep(1)
#                 f.write(response.text)
#         if current_page == 3:
#             time.sleep(1)
#             file_name = f'3_response_{return_parse_date()}.txt'.replace(':', '_').replace(' ', '_')
#             with open(file_name, 'w') as f:
#                 time.sleep(1)
#                 f.write(response.text)
#         next_page = combo.minfo.get_next_page
#         print(f'current page - {current_page}; next page {next_page}')
#         if next_page:
#             current_page_arg += 1
#             if int(next_page) < 3:
#                 num_page = 0
#                 print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&', num_page)
#             else:
#                 num_page = int(next_page) - 2
#                 print('$$$$$$$$$$$$$$$$$$$$$$$, This is  num_page WHEN ELSE', num_page)
#             p_data_new = p_data
#             p_data_new[''] = ''
#             p_data_new['__EVENTTARGET'] = combo.minfo.get_EVENTTARGET_from_tag(combo.minfo.return_tag_a_pagination)
#             # p_data_new['__EVENTARGUMENT'] = combo.minfo.get_EVENTARGUMENT_from_tag(combo.minfo.return_tag_a_pagination)
#             p_data_new['__EVENTARGUMENT'] = f'Page${next_page}'
#             p_data_new['ctl00$PrivateOffice1$ctl00'] = post_privat_office + '|' + p_data['__EVENTTARGET']
#             url = self.url_spider.return_url_param(message_page, param)
#             request_headers_msg[':path'] = '/' + url.split('/')[-1]
#             request_headers_msg['cookie'] = ''.join(
#                 re.sub(r'PageNumber=\d{1,2}', f'PageNumber={num_page}', only_cookie, flags=re.I))
#             # print(f"This is request_headers_msg {request_headers_msg['cookie']}\n\n")
#             request_headers_msg['referer'] = response.url
#             request_headers_msg['user-agent'] = p_headers['user-agent']
#             coordinate_x = dict(p_data_new).get('ctl00$cphBody$ibMessagesSearch.x', None)
#             coordinate_y = dict(p_data_new).get('ctl00$cphBody$ibMessagesSearch.y', None)
#             if coordinate_x is not None:
#                 # delete this param because it's not necessary
#                 del p_data_new['ctl00$cphBody$ibMessagesSearch.x']
#             if coordinate_y is not None:
#                 # delete this param because it's not necessary
#                 del p_data_new['ctl00$cphBody$ibMessagesSearch.y']
#             # logger.info(f'post data for the next page::\n{p_data_new}\n')
#             print(f'DATA FOR REQUESTS:::\n{request_headers_msg}\n{p_data_new}\n\n')
#             if next_page == int(current_page_arg):
#                 yield SplashFormRequest(url,
#                                         callback=self.serp_of_msg,
#                                         endpoint='execute',
#                                         cache_args=['lua_source'], args={'lua_source': script_lua_category},
#                                         slot_policy=SlotPolicy.PER_DOMAIN,
#                                         dont_filter=False,
#                                         # cookies=cookie_parser(request_headers_msg['cookie']),
#                                         splash_headers=request_headers_msg,
#                                         formdata=p_data_new,
#                                         cb_kwargs={'p_headers': request_headers_msg,
#                                                    'p_data': p_data_new,
#                                                    'msg_type': msg_type,
#                                                    'only_cookie': request_headers_msg['cookie'],
#                                                    'current_page_arg': current_page_arg
#                                                    })

