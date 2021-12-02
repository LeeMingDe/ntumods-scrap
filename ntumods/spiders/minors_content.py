import scrapy
from scrapy_splash import SplashRequest
import time

class MinorsContentSpider(scrapy.Spider):
    name = 'minors_content'
    allowed_domains = ['wish.wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main']
    counter = 479
    repeat_counter = 0
    prevCourseName = ""
    currentCourseName = ""
    iframe_line = 'iframe = function() { var f = document.getElementsByTagName("iframe")[0].contentDocument; return f.getElementsByTagName("body")[0].innerHTML; }'
    
    def script(self, number):
        return """
            function main(splash, args)
                assert(splash:go(args.url))
                assert(splash:wait(0.25))
                select_xpath = assert(splash:select('select[name="r_course_yr"]'))
                select_xpath:mouse_click()
                {0}
                assert(splash:wait(0.40))
                splash:send_keys("<Enter>")
                assert(splash:wait(0.25))
                load_btn = assert(splash:select('input[type=button]:nth-child(4)'))
                load_btn.mouse_click()
                assert(splash:wait(0.25))

                splash:set_viewport_full()
                
                splash:runjs('iframe = function() {{ var f = document.getElementsByTagName("iframe")[0].contentDocument; return f.getElementsByTagName("body")[0].innerHTML; }}')
                local result = splash:evaljs("iframe()")
                return result
            end
        """.format('splash:send_keys("<Down>")' * number)

    def start_requests(self):
        yield SplashRequest(url="https://wish.wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main", callback=self.parse,
            endpoint="execute", args={'lua_source': self.script(self.counter)}, headers= {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
            }
        )

    def parse(self, response):
        current_table_xpath = response.xpath('//html/body/center/table/tbody')
        table_row_counter = 2

        while current_table_xpath.xpath(f'.//tr[{table_row_counter}]').get() is not None:
            module_details = {
                'course_name': response.xpath('//center/font[1]/b/b/font/text()').get(),
                'module_code': current_table_xpath.xpath(f".//tr[{table_row_counter}]/td[1]/b/font/text()").get(),
                'module_name': current_table_xpath.xpath(f".//tr[{table_row_counter}]/td[2]/b/font/text()").get(),
                'module_units': current_table_xpath.xpath(f"normalize-space(.//tr[{table_row_counter}]/td[3]/b/font/text())").get(),
                'dept_maintain': current_table_xpath.xpath(f"(.//tr[{table_row_counter}]/td[4]/b/font/text())").get(),
            }
            table_row_counter += 1

            while current_table_xpath.xpath(f'.//tr[{table_row_counter}]/td/text()').get() != " ":
                row_label = current_table_xpath.xpath(f".//tr[{table_row_counter}]/td[1]/b/font/text()").get()
                row_content = current_table_xpath.xpath(f'.//tr[{table_row_counter}]/td[2]/b/font/text()').get()

                if current_table_xpath.xpath(f'.//tr[{table_row_counter}]/td[2]/b/font/text()').get() == current_table_xpath.xpath('.//tr[last()]/td[2]/b/font/text()').get():
                    module_details['module_description'] = current_table_xpath.xpath(f'normalize-space(.//tr[{table_row_counter}]/td/font/text())').get()
                    table_row_counter += 1
                    continue

                if row_content is None:
                    table_row_counter += 1
                    continue

                if row_label in module_details:
                    module_details[f"{row_label}"]  = module_details[f"{row_label}"] + " " + row_content

                else:
                    module_details[f"{row_label}"]  = row_content
                
                if row_label == "Prerequisite:":
                    while "OR" in row_content:
                        table_row_counter += 1
                        row_content = current_table_xpath.xpath(f'.//tr[{table_row_counter}]/td[2]/b/font/text()').get()
                        if row_content is None:
                            break
                        module_details[f"{row_label}"]  = module_details[f"{row_label}"] + " " + row_content
                table_row_counter += 1
            table_row_counter += 1
            time.sleep(0.75)
            yield module_details


        if self.prevCourseName != "" and self.currentCourseName != "":
            self.prevCourseName = self.currentCourseName
            self.currentCourseName = response.xpath("//center/font[1]/b/b/font/text()").get()

        elif self.prevCourseName != "" and self.currentCourseName == "":
            self.currentCourseName = response.xpath("//center/font[1]/b/b/font/text()").get()

        elif self.prevCourseName == "":
            self.prevCourseName = response.xpath("//center/font[1]/b/b/font/text()").get()

        if self.repeat_counter > 2:
            return

        if self.prevCourseName == self.currentCourseName:
            self.repeat_counter += 1
        else:
            self.repeat_counter = 0

        self.counter += 1
        yield SplashRequest(url="https://wish.wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main", callback=self.parse,
            endpoint="execute", args={'lua_source': self.script(self.counter)}, headers= {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        }, dont_filter=True)
