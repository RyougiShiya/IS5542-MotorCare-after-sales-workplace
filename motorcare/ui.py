import json
from pathlib import Path
import gradio as gr
from .engine import ROOT, MODEL, DemoError, analyze, configured, message

from .paths import CASES_DIR

CASES=json.loads((CASES_DIR/'cases.json').read_text())
TEXT={
'English': dict(title='# MotorCare · After-sales assistant',intro='BLM230-A2 motor + BMUD30-C2 driver · AL46 / AL30 / AL28 initial triage\n\nFor after-sales engineers and maintenance technicians. Engineers review recommendations and confirm outcomes. One ticket per fault; up to 3 images in total.',device='Device',chat='Service ticket',input='Describe the fault or add follow-up information',placeholder='Describe what happened, when it started and any checks already performed…',send='Send',new='New ticket',examples='Demo examples · selecting one starts a new ticket',names=['Power-on alarm · AL46','Overload · AL30','Sensor error · AL28'],ready='Ready. Local configuration detected; connectivity not yet verified.',missing='Fill in the local .env and restart to enable analysis.',sample='Simulated ticket and alarm illustration, not a real fault photograph. Equipment models are supplied by the scenario.',changed='Interface updated. Earlier messages keep their original language; new answers use English.'),
'中文': dict(title='# MotorCare · 售后辅助',intro='BLM230-A2 电机 + BMUD30-C2 驱动器 · AL46 / AL30 / AL28 初步排查\n\n供售后工程师与维修人员使用，由工程师复核建议并确认处理结果。一个工单处理一件故障，累计最多 3 张图片。',device='设备型号',chat='工单对话',input='描述故障或补充信息',placeholder='请描述故障现象、发生时间和已完成的检查……',send='发送',new='新建工单',examples='演示案例 · 选择后开始新工单',names=['上电报警 · AL46','过载 · AL30','传感器异常 · AL28'],ready='本地配置已填写，接口连通性尚待验证。',missing='请填写本地 .env 并重启以启用分析。',sample='模拟工单及报警示意图，不是真实故障照片。设备型号来自场景设定。',changed='界面已切换；历史消息保留原语言，后续回答使用中文。')}
def status(lang): return TEXT[lang]['ready' if configured() else 'missing']
def empty(): return {'text':'','files':[]}
def submit(value,history,display,lang):
    value=value or empty(); paths=[x if isinstance(x,str) else x['path'] for x in value.get('files',[])]
    try: result,updated=analyze(value.get('text',''),paths,history,lang)
    except DemoError as e: return value,history,display,message(str(e),lang)
    messages=list(display)
    for p in paths: messages.append({'role':'user','content':gr.Image(value=p,show_label=False)})
    if value.get('text','').strip(): messages.append({'role':'user','content':value['text']})
    messages.append({'role':'assistant','content':result})
    return empty(),updated,messages,''
def load_case(index,lang):
    c=CASES[index]
    return {'text':c['input_zh' if lang=='中文' else 'input_en'],'files':[str(CASES_DIR/x) for x in c['images']]},[],[],TEXT[lang]['sample'],TEXT[lang]['sample'],index
def load_followup(lang,index):
    if index is None: return gr.skip()
    return {'text':CASES[index]['followup_zh' if lang=='中文' else 'followup_en'],'files':[]}

def reset(lang): return empty(),[],[],'',status(lang),None

def summarize(history,display,lang):
    if not history:
        return display, ('请先提交故障信息，完成分析后再生成摘要。' if lang=='中文' else 'Submit fault information and complete an analysis before generating a summary.')
    instruction = ('请仅根据当前工单生成处理摘要，依次包含：设备及故障、客户反馈与图片观察、工程师报告的检查发现、已执行措施、当前结果、未确认事项与下一步、相关来源。严格区分建议与已执行操作。没有明确恢复确认则写待确认，不得认定已解决。不要增加新的诊断或操作建议。' if lang=='中文' else 'Summarize this ticket only: equipment and fault; customer reports and image observations; engineer-reported findings; explicitly completed actions; current outcome; unknowns and next steps; sources. Keep proposals separate from completed actions. Without explicit recovery confirmation, mark the outcome unconfirmed, never resolved. Add no new diagnosis or procedures.')
    try:
        result,_=analyze(instruction,[],history,lang)
    except DemoError as e:
        return display,message(str(e),lang)
    # Summary is a view of evidence, not new evidence in the diagnostic history.
    return [*display,{'role':'assistant','content':('## 工单摘要\n\n' if lang=='中文' else '## Ticket summary\n\n')+result}], ('摘要已生成；仅包含已提交的信息，请工程师复核。' if lang=='中文' else 'Summary generated from submitted information only. Engineer review required.')

def summarize_visible(history,display,lang):
    if not history:
        warning=('请先发送故障信息。仅加载案例但未发送时，还没有可整理的工单。' if lang=='中文' else 'Send the fault information first. Loading an example alone does not create a submitted ticket.')
        gr.Warning(warning)
        yield gr.skip(),warning,warning
        return
    waiting='正在生成摘要，请稍候……' if lang=='中文' else 'Generating ticket summary…'
    yield gr.skip(),waiting,waiting
    messages,status_text=summarize(history,display,lang)
    if len(messages)==len(display):
        gr.Warning(status_text)
        yield gr.skip(),status_text,status_text
    else:
        yield gr.skip(),status_text,messages[-1]['content']


def submit_record(value,history,display,lang):
    result=submit(value,history,display,lang)
    changed=len(result[1])>len(history)
    note=('工单信息已更新，请重新整理记录。旧记录仅供参考。' if lang=='中文' else 'Ticket information changed. Update the record; any previous record is outdated.')
    return (*result,note if changed else gr.skip())

def record_view(history,display,lang):
    if not history:
        yield gr.update(selected='record'), ('请先在故障排查中发送信息并完成分析。' if lang=='中文' else 'Submit fault information and complete an analysis in Troubleshooting first.'),gr.skip()
        return
    yield gr.update(selected='record'), ('正在整理工单记录……' if lang=='中文' else 'Preparing ticket record…'),gr.skip()
    messages,status_text=summarize(history,display,lang)
    yield gr.update(selected='record'),status_text,(messages[-1]['content'] if len(messages)>len(display) else gr.skip())


# Only verified combinations are selectable. Extend alongside knowledge and tests.
EQUIPMENT = {'BLM230-A2': ['BMUD30-C2']}

def driver_choices(motor):
    return EQUIPMENT.get(motor, [])

def valid_equipment(motor, driver):
    return driver in driver_choices(motor)

def source_links(display, lang):
    import re
    from .paths import KNOWLEDGE_DIR
    sources=json.loads((KNOWLEDGE_DIR/'sources.json').read_text())
    cited=set()
    for msg in display:
        if msg['role']=='assistant' and isinstance(msg['content'],str):
            cited.update(re.findall(r'\[(M\d+)(?:,[^\]]*)?\]',msg['content']))
    rows=[f"- [{s['source_id']}] [{s['title']}]({s['url']})" for s in sources if s['source_id'] in cited]
    return '\n'.join(rows) or ('分析后将在此显示引用来源。' if lang=='中文' else 'Cited references will appear here after analysis.')

def build():
    assets=Path(__file__).parent/'assets'
    with gr.Blocks(title='MotorCare',theme=gr.themes.Soft(primary_hue='teal',neutral_hue='slate',font=['Arial','PingFang SC','Microsoft YaHei','sans-serif'],font_mono=['Arial','PingFang SC','Microsoft YaHei','sans-serif']),css=(assets/'workspace.css').read_text(),js=(assets/'workspace.js').read_text(),analytics_enabled=False,fill_width=True) as demo:
        history=gr.State([]); selected_case=gr.State(None); pending=gr.State(None)
        committed=gr.State(('BLM230-A2','BMUD30-C2'))
        with gr.Row(elem_id='mc-header'):
            brand=gr.Markdown('## ◈ MotorCare\nAfter-sales workspace',elem_id='mc-brand')
            lang=gr.Dropdown(['English','中文'],value='English',show_label=False,container=False,scale=0,min_width=140,interactive=True,elem_id='mc-language')
        with gr.Row(elem_id='mc-layout'):
            with gr.Column(scale=1,min_width=230,elem_id='mc-sidebar'):
                new=gr.Button('+ New ticket',variant='primary')
                equipment_title=gr.Markdown('### Equipment')
                motor=gr.Dropdown(list(EQUIPMENT),value='BLM230-A2',label='Motor',interactive=True)
                driver=gr.Dropdown(driver_choices('BLM230-A2'),value='BMUD30-C2',label='Driver',interactive=True)
                review=gr.Markdown('Engineer review required',elem_id='mc-review')
            with gr.Column(scale=5,min_width=500,elem_id='mc-main'):
                with gr.Group(visible=False,elem_id='mc-confirm') as confirm_panel:
                    confirmation=gr.Markdown('Start a new ticket? This clears the current conversation, draft and record. / 开启新工单？将清除当前对话、草稿及记录。')
                    with gr.Row():
                        accept=gr.Button('Confirm / 确认',variant='primary')
                        cancel=gr.Button('Cancel / 取消')
                with gr.Tabs(selected='triage') as workspace:
                    with gr.Tab('Troubleshooting',id='triage') as triage_tab:
                        with gr.Row(elem_id='mc-toolbar'):
                            work_title=gr.Markdown('### Fault investigation')
                            summary=gr.Button('Prepare ticket record',scale=0,min_width=200)
                        chat=gr.Chatbot(type='messages',label='Service ticket',show_label=False,height=480,sanitize_html=True,allow_tags=False,elem_id='mc-chat')
                        with gr.Accordion('Knowledge sources',open=False) as source_panel:
                            sources=gr.Markdown(source_links([],'English'))
                        box=gr.MultimodalTextbox(file_types=['.jpg','.jpeg','.png','.webp'],file_count='multiple',sources=['upload'],show_label=False,placeholder=TEXT['English']['placeholder'],submit_btn='Send',max_plain_text_length=8000,elem_id='mc-composer')
                        info=gr.Markdown(status('English'),elem_id='mc-status')
                    with gr.Tab('Ticket record',id='record') as record_tab:
                        with gr.Row():
                            refresh=gr.Button('Update ticket record')
                            back=gr.Button('Back to troubleshooting')
                        record_status=gr.Markdown('No record yet. Prepare a record after submitting fault information.')
                        summary_result=gr.Textbox(label='Ticket record',lines=20,interactive=False,show_copy_button=True)
        # CSS/JS hides this panel visually; it is not an authorization boundary.
        with gr.Column(elem_id='mc-demo'):
            drag=gr.Markdown('**Demo tools / 演示工具**　⋮⋮',elem_id='mc-drag')
            close_demo=gr.Button('Close / 关闭',size='sm')
            buttons=[gr.Button(x,size='sm') for x in TEXT['English']['names']]
            followup=gr.Button('Fill follow-up example',size='sm')
            notice=gr.Markdown('Simulated examples · Alt/Option + Shift + D')

        opts=dict(api_name=False,concurrency_id='ticket',concurrency_limit=1)
        # Atomic transition results, shared by new-ticket, case and device changes.
        reset_outputs=[box,history,chat,notice,info,selected_case,summary_result,record_status,workspace,sources,pending,confirm_panel,motor,driver,committed]
        def transition(action,language):
            pair=action.get('equipment',('BLM230-A2','BMUD30-C2'))
            base=load_case(action['index'],language) if action['kind']=='case' else reset(language)
            return (*base,'','',gr.update(selected='triage'),source_links([],language),None,gr.update(visible=False),gr.update(value=pair[0]),gr.update(choices=driver_choices(pair[0]),value=pair[1]),pair)
        def request_transition(action,h,value,language,pair):
            action={**action,'equipment':action.get('equipment',pair)}
            if h or (value and (value.get('text') or value.get('files'))):
                result=[gr.skip() for _ in reset_outputs]
                result[10]=action;result[11]=gr.update(visible=True)
                result[12]=gr.update(value=pair[0]);result[13]=gr.update(choices=driver_choices(pair[0]),value=pair[1])
                return tuple(result)
            return transition(action,language)
        for i,b in enumerate(buttons):
            def choose(h,value,language,pair,index=i):
                return request_transition({'kind':'case','index':index},h,value,language,pair)
            b.click(choose,[history,box,lang,committed],reset_outputs,**opts)
        new.click(lambda h,v,l,p:request_transition({'kind':'new'},h,v,l,p),[history,box,lang,committed],reset_outputs,**opts)
        accept.click(lambda action,l: transition(action,l) if action else tuple(gr.skip() for _ in reset_outputs),[pending,lang],reset_outputs,**opts)
        cancel.click(lambda:(None,gr.update(visible=False)),outputs=[pending,confirm_panel],**opts)
        def motor_changed(m,h,v,l,p):
            choices=driver_choices(m)
            if not choices:
                gr.Warning('Unsupported equipment / 不支持的设备')
                return tuple(gr.skip() if i not in (12,13) else (gr.update(value=p[0]) if i==12 else gr.update(choices=driver_choices(p[0]),value=p[1])) for i in range(len(reset_outputs)))
            pair=(m,choices[0])
            return request_transition({'kind':'new','equipment':pair},h,v,l,p) if pair!=tuple(p) else tuple(gr.skip() for _ in reset_outputs)
        motor.input(motor_changed,[motor,history,box,lang,committed],reset_outputs,**opts)
        def driver_changed(d,m,h,v,l,p):
            if not valid_equipment(m,d): return motor_changed('',h,v,l,p)
            return request_transition({'kind':'new','equipment':(m,d)},h,v,l,p) if (m,d)!=tuple(p) else tuple(gr.skip() for _ in reset_outputs)
        driver.input(driver_changed,[driver,motor,history,box,lang,committed],reset_outputs,**opts)
        def send(value,h,display,language,m,d,p):
            if not valid_equipment(m,d) or (m,d)!=tuple(p):
                return value,h,display,'Unsupported equipment / 不支持的设备组合',gr.skip(),gr.skip()
            result=submit_record(value,h,display,language)
            return (*result,source_links(result[2],language))
        box.submit(send,[box,history,chat,lang,motor,driver,committed],[box,history,chat,info,record_status,sources],**opts)
        summary.click(record_view,[history,chat,lang],[workspace,record_status,summary_result],**opts)
        refresh.click(record_view,[history,chat,lang],[workspace,record_status,summary_result],**opts)
        back.click(lambda:gr.update(selected='triage'),outputs=workspace,api_name=False,queue=False)
        followup.click(load_followup,[lang,selected_case],[box],**opts)
        close_demo.click(fn=None,js="() => window.mcDemoToggle(false)",api_name=False,queue=False)
        def translate(language,current_notice,display):
            zh=language=='中文';t=TEXT[language]
            return (gr.update(value='+ 新建工单' if zh else '+ New ticket'),'### 设备信息' if zh else '### Equipment',gr.update(label='电机型号' if zh else 'Motor'),gr.update(label='驱动器型号' if zh else 'Driver'),'需工程师复核' if zh else 'Engineer review required',gr.update(label='故障排查' if zh else 'Troubleshooting'),gr.update(label='工单记录' if zh else 'Ticket record'),'### 故障排查' if zh else '### Fault investigation',gr.update(value='整理工单记录' if zh else 'Prepare ticket record'),gr.update(placeholder=t['placeholder'],submit_btn=t['send']),'',gr.update(label='知识来源' if zh else 'Knowledge sources'),source_links(display,language),gr.update(label='工单记录' if zh else 'Ticket record'),gr.update(value='更新工单记录' if zh else 'Update ticket record'),gr.update(value='返回故障排查' if zh else 'Back to troubleshooting'),*[gr.update(value=x) for x in t['names']],gr.update(value='填入补充信息示例' if zh else 'Fill follow-up example'),t['sample'] if current_notice else '')
        lang.change(translate,[lang,notice,chat],[new,equipment_title,motor,driver,review,triage_tab,record_tab,work_title,summary,box,info,source_panel,sources,summary_result,refresh,back,*buttons,followup,notice],**opts)
    return demo
