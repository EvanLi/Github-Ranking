# -*- coding: utf-8 -*-
from datetime import datetime
import os
from process import Processor,ProcessorGQL

if __name__=="__main__":
    t1 = datetime.now()

    ROOT_PATH = os.path.abspath(os.path.join(__file__,"../../"))
    os.chdir(os.path.join(ROOT_PATH,'source'))

    # processor = Processor() # use Github REST API v3
    processor = ProcessorGQL() # use Github GraphQL API v4
    print("Write head and contents of README.md!")
    processor.write_head_contents()
    print("write to readme and languages.md")
    processor.write_readme_lang_md()
    print("Save data to csv file")
    processor.save_to_csv()

    print("Total time: {}s".format((datetime.now()-t1).total_seconds()))