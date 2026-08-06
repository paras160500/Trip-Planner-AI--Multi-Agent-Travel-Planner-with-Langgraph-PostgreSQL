# from tools.tavily_tool import tavily_search

# res = tavily_search("Best Hotels in India")
# print(res)

from tools.flight_tool import search_flights
res = search_flights("Plan a 7 days Japan trip from usa")
print(res)