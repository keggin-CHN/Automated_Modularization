这个文档是为auto.py所写.C:\code\scraper.py是爬虫脚本，auto.py是自动答题脚本。
假设base url是http://202.119.208.14
那么http://202.119.208.14/talk/ExaminationList.jspx?type=1是我们需要的页面.这个页面上有考试列表，抓包的结果是这样的。HTTP/1.1 200
Content-Type: text/html;charset=UTF-8
Transfer-Encoding: chunked
Date: Fri, 16 Jan 2026 05:11:41 GMT

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"><head id="j_idt2"><link type="text/css" rel="stylesheet" href="/javax.faces.resource/theme.css.jspx?ln=primefaces-south-street" /><link type="text/css" rel="stylesheet" href="/javax.faces.resource/fa/font-awesome.css.jspx?ln=primefaces&amp;v=6.2" /><link type="text/css" rel="stylesheet" href="/javax.faces.resource/components.css.jspx?ln=primefaces&amp;v=6.2" /><script type="text/javascript" src="/javax.faces.resource/jquery/jquery.js.jspx?ln=primefaces&amp;v=6.2"></script><script type="text/javascript" src="/javax.faces.resource/jquery/jquery-plugins.js.jspx?ln=primefaces&amp;v=6.2"></script><script type="text/javascript" src="/javax.faces.resource/core.js.jspx?ln=primefaces&amp;v=6.2"></script><script type="text/javascript" src="/javax.faces.resource/components.js.jspx?ln=primefaces&amp;v=6.2"></script><link type="text/css" rel="stylesheet" href="/javax.faces.resource/watermark/watermark.css.jspx?ln=primefaces&amp;v=6.2" /><script type="text/javascript" src="/javax.faces.resource/watermark/watermark.js.jspx?ln=primefaces&amp;v=6.2"></script><script type="text/javascript">if(window.PrimeFaces){PrimeFaces.settings.locale='zh';}</script><!--[if lte IE 7]>
        <script>
            window.location.href = '/update_browser.jsp';
        </script><![endif]-->
        <title>考试列表
            - 南京林业大学思想政治理论课过程考核管理系统</title>
        <meta http-equiv="keywords" content=" 南京林业大学思想政治理论课过程考核管理系统" />
        <meta http-equiv="description" content=" 南京林业大学思想政治理论课过程考核系统" />
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=Edge,chrome=1" />
        <link rel="stylesheet" type="text/css" href="/resources/css/rerebbs.css" />
        <link rel="stylesheet" type="text/css" href="/resources/css/rerebbs_a.css" />
        <link rel="stylesheet" type="text/css" href="/resources/jquery.Sonline.2.0/style/default_blue.css" /></head><body style="background-color: #;">
<form id="myForm" name="myForm" method="post" action="/talk/ExaminationList.jspx" enctype="application/x-www-form-urlencoded">
<input type="hidden" name="myForm" value="myForm" />
<div id="myForm:login1" class="ui-dialog ui-widget ui-widget-content ui-corner-all ui-shadow ui-hidden-container" style="z-index: 1000;"><div class="ui-dialog-titlebar ui-widget-header ui-helper-clearfix ui-corner-top"><span id="myForm:login1_title" class="ui-dialog-title">登录</span><a href="#" class="ui-dialog-titlebar-icon ui-dialog-titlebar-close ui-corner-all" aria-label="Close"><span class="ui-icon ui-icon-closethick"></span></a></div><div class="ui-dialog-content ui-widget-content"><div id="myForm:j_idt12" class="ui-outputpanel ui-widget">
                    <script>
                        function testLogin() {
                            //alert('ok');
                            if (true ==true)
                            {
                                PF('login1').hide();

                            }
                            PF('loginButton').enable();

                        }
                    </script></div><table style="width:98%;margin: 5px 0px 15px 0px;height:130px;">
<tbody>
<tr>
<td class="w21"><span class="myTip">标识类型：</span><select name="myForm:j_idt17" size="1">	<option value="urn" selected="selected">用户名</option>
</select></td>
</tr>
<tr>
<td class="w21"><script id="myForm:j_idt19_s" type="text/javascript">$(function(){PrimeFaces.cw("Watermark","widget_myForm_j_idt19",{id:"myForm:j_idt19",value:"考生标识",target:"myForm:urn"});});</script><input id="myForm:urn" name="myForm:urn" type="text" value="" autocomplete="off" onfocus="this.select()" style="" class="ui-inputfield ui-inputtext ui-widget ui-state-default ui-corner-all inputTextQ" /><script id="myForm:urn_s" type="text/javascript">PrimeFaces.cw("InputText","widget_myForm_urn",{id:"myForm:urn"});</script></td>
</tr>
<tr>
<td class="w21"><script id="myForm:j_idt20_s" type="text/javascript">$(function(){PrimeFaces.cw("Watermark","widget_myForm_j_idt20",{id:"myForm:j_idt20",value:"密码",target:"myForm:pwd"});});</script><input id="myForm:pwd" name="myForm:pwd" type="password" class="ui-inputfield ui-password ui-widget ui-state-default ui-corner-all inputTextQ" autocomplete="off" onfocus="this.select()" /><script id="myForm:pwd_s" type="text/javascript">$(function(){PrimeFaces.cw("Password","widget_myForm_pwd",{id:"myForm:pwd"});});</script></td>
</tr>
<tr>
<td class="w21"><table cellpadding="0" cellspacing="0" style="width:100%;margin-top: 10px;">
<tbody>
<tr>
<td><button id="myForm:j_idt22" name="myForm:j_idt22" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" onclick="PrimeFaces.bcn(this,event,[function(event){PF('loginButton').disable();},function(event){PrimeFaces.ab({s:&quot;myForm:j_idt22&quot;,p:&quot;myForm&quot;,u:&quot;myForm:mainPanel&quot;,onco:function(xhr,status,args){javascript:testLogin();;}});return false;}]);" style="width:80px;" type="submit"><span class="ui-button-text ui-c">登录</span></button><script id="myForm:j_idt22_s" type="text/javascript">PrimeFaces.cw("CommandButton","loginButton",{id:"myForm:j_idt22"});</script></td>
<td><input type="checkbox" name="myForm:j_idt24" />七天内自动登录</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
<hr id="myForm:j_idt26" class="ui-separator ui-state-default ui-corner-all" /><table style="width:100%;">
<tbody>
<tr>
<td><label>还没有帐号？</label>   
                    <a href="/talk/Register3.xhtml">立即注册</a></td>
<td><a href="/talk/GetPWD.xhtml">忘记密码？</a></td>
</tr>
</tbody>
</table>
<div id="myForm:j_idt35" class="ui-outputpanel ui-widget"></div></div></div><script id="myForm:login1_s" type="text/javascript">$(function(){PrimeFaces.cw("Dialog","login1",{id:"myForm:login1",resizable:false,width:"400",showEffect:"drop",hideEffect:"drop"});});</script><div id="myForm:mainFrontMenuWrapper" class="ui-panel ui-widget ui-widget-content ui-corner-all" style="border:0px solid red;border-bottom: 1px solid #bcc7cf;border-radius: 0px;" data-widget="widget_myForm_mainFrontMenuWrapper"><div id="myForm:mainFrontMenuWrapper_content" class="ui-panel-content ui-widget-content">  
                <div style="width:970px;margin: 0px auto!important;border-radius: 3px;height: 75px;border:0px solid red;">
                    <div style="width:280px;border:0px solid green;height:75px;float: left;overflow: hidden;"><a href="#" target="_blank"><img id="myForm:adv2" src="servlet/ShowAbstractImage?id=a0312bb5-64bd-4439-a61a-b739169b1d87" style="width:100%;margin: 0px 0px 0px 0px;border:0px 0px 0px 0px;" /></a>
                    </div>

                    <div style="border:0px solid red;width:680px;float:right;">
                        <div><div id="myForm:j_idt40" class="ui-outputpanel ui-widget"><table style="text-align: center;width: 100%;border:0px solid green;">
<tbody>
<tr>
<td><span class="topTip">欢迎您 周文杰！</span></td>
<td><div id="myForm:front_menu" class="ui-menu ui-menubar ui-widget ui-widget-content ui-corner-all ui-helper-clearfix front_menu" style="background:transparent!important;" role="menubar"><div tabindex="0" class="ui-helper-hidden-accessible"></div><ul class="ui-menu-list ui-helper-reset"><li class="ui-menuitem ui-widget ui-corner-all" role="menuitem"><a tabindex="-1" class="ui-menuitem-link ui-corner-all topNav newMenuNav" href="#" onclick="PrimeFaces.ab({s:&quot;myForm:j_idt52&quot;,f:&quot;myForm&quot;});return false;"><span class="ui-menuitem-text"><img id="myForm:j_idt53" src="/resources/images/svgs/icons/internal.svg?pfdrid_c=true" alt="" class="menuSvg" />
                                                <br /> 退出</span></a></li><li class="ui-menuitem ui-widget ui-corner-all" role="menuitem"><a tabindex="-1" id="myForm:results" class="ui-menuitem-link ui-corner-all topNav newMenuNav" href="#" onclick="PrimeFaces.ab({s:&quot;myForm:results&quot;,f:&quot;myForm&quot;});return false;"><span class="ui-menuitem-text"><img id="myForm:j_idt63" src="/resources/images/svgs/icons/picture.svg?pfdrid_c=true" alt="" class="menuSvg" />
                                                <br />考试结果</span></a></li><li class="ui-menuitem ui-widget ui-corner-all" role="menuitem"><a tabindex="-1" class="ui-menuitem-link ui-corner-all topNav" href="/talk/Default.jspx"><span class="ui-menuitem-text"><img id="myForm:j_idt67" src="/resources/images/svgs/icons/engineering.svg?pfdrid_c=true" alt="" class="menuSvg" />
                                            <br /> 系统首页</span></a></li></ul></div><script id="myForm:front_menu_s" type="text/javascript">PrimeFaces.cw("Menubar","widget_myForm_front_menu",{id:"myForm:front_menu",autoDisplay:true});</script></td>
</tr>
</tbody>
</table>
<div id="myForm:qrPanel" class="ui-overlaypanel ui-widget ui-widget-content ui-overlay-hidden ui-corner-all ui-shadow" style=""><div class="ui-overlaypanel-content">
                                    <div style="width:200px!important;border:0px solid red;text-align: center;"><span class="topTip">手机扫一扫！</span><a href="/mobile/Default.jspx" title="点击进入"><img id="myForm:j_idt73" src="/servlet/QRCodeServlet.png?pfdrid_c=true" alt="" style="width:200px;" /></a>
                                    </div></div></div><script id="myForm:qrPanel_s" type="text/javascript">$(function(){PrimeFaces.cw("OverlayPanel","widget_myForm_qrPanel",{id:"myForm:qrPanel",target:"myForm:mobile",showEvent:"mouseover",showEffect:"blind",hideEffect:"explode"});});</script><div id="myForm:resultsPanel" class="ui-overlaypanel ui-widget ui-widget-content ui-overlay-hidden ui-corner-all ui-shadow" style=""><div class="ui-overlaypanel-content">
                                    <div style="width:150px!important;border:0px solid red;text-align: center;"><div id="myForm:j_idt76" class="ui-menu ui-widget ui-widget-content ui-corner-all ui-helper-clearfix menuPanel" style="background-color: transparent!important;" role="menu"><div tabindex="0" class="ui-helper-hidden-accessible"></div><ul class="ui-menu-list ui-helper-reset"><li class="ui-menuitem ui-widget ui-corner-all" role="menuitem"><a tabindex="-1" class="ui-menuitem-link ui-corner-all" href="/talk/ExamCaseReportList.jspx?type=1"><span class="ui-menuitem-text">正式考试</span></a></li><li class="ui-menuitem ui-widget ui-corner-all" role="menuitem"><a tabindex="-1" class="ui-menuitem-link ui-corner-all" href="/talk/ExamCaseReportList.jspx?type=2"><span class="ui-menuitem-text">模拟考试</span></a></li><li class="ui-separator ui-state-default"></li></ul></div><script id="myForm:j_idt76_s" type="text/javascript">$(function(){PrimeFaces.cw("PlainMenu","widget_myForm_j_idt76",{id:"myForm:j_idt76"});});</script>
                                    </div></div></div><script id="myForm:resultsPanel_s" type="text/javascript">$(function(){PrimeFaces.cw("OverlayPanel","resultsPanel",{id:"myForm:resultsPanel",target:"myForm:results",showEvent:"mouseover",hideEvent:"mousedown",onShow:function(){PF('userCenterPanel').hide();}});});</script></div>
                        </div>
                        <div style="clear:both;"></div>
                    </div>
                </div></div></div><script id="myForm:mainFrontMenuWrapper_s" type="text/javascript">PrimeFaces.cw("Panel","widget_myForm_mainFrontMenuWrapper",{id:"myForm:mainFrontMenuWrapper"});</script>
            <div style="height:20px;background: white; "></div>
            
            <div style="width:100%;background: white; ">
                <div style="margin: 0px auto;width:990px;" class="ui-grid ui-grid-fixed"><div id="myForm:mainPanel" class="ui-panel ui-widget ui-widget-content ui-corner-all mainPanel" style="border:0px solid #e5e5e5;width:100%;background: transparent;" data-widget="widget_myForm_mainPanel"><div id="myForm:mainPanel_content" class="ui-panel-content ui-widget-content">
                <script type="text/javascript" language="javascript">
                    function aabbcc(url) {
                        var scrWidth = screen.availWidth;
                        var scrHeight = screen.availHeight;
                        var self = window.open(url, '', "fullscreen=3,resizable=false,toolbar=no,menubar=no,scrollbars=yes,location=no,top=0,left=0,width=" + scrWidth + ",height=" + scrHeight);
                        //self.resizeTo(scrWidth,scrHeight);
                        self.moveTo(0, 0);
                    }

                </script><div id="myForm:topNav8" class="ui-panel ui-widget ui-widget-content ui-corner-all frontColumn topNav8Wrapper" style="margin-bottom: 10px!important;" data-widget="widget_myForm_topNav8"><div id="myForm:topNav8_content" class="ui-panel-content ui-widget-content"><a href="Default.jspx" class="nav8">首页</a><span class="navSeparator">/</span><span class="nav8">考试</span><span class="navSeparator">/</span><span class="nav8">正式考试</span></div></div><script id="myForm:topNav8_s" type="text/javascript">PrimeFaces.cw("Panel","widget_myForm_topNav8",{id:"myForm:topNav8"});</script><div id="myForm:j_idt109" class="ui-panel ui-widget ui-widget-content ui-corner-all frontColumn  noBackground" style="margin-bottom: 10px;" data-widget="widget_myForm_j_idt109"><div id="myForm:j_idt109_content" class="ui-panel-content ui-widget-content"><table>
<tbody>
<tr><td></td></tr></tbody>
</table>
<table>
<tbody>
<tr><td></td></tr></tbody>
</table>
</div></div><script id="myForm:j_idt109_s" type="text/javascript">PrimeFaces.cw("Panel","widget_myForm_j_idt109",{id:"myForm:j_idt109"});</script><div id="myForm:examDc" class="ui-datatable ui-widget frontColumn noBackgroundGrid" style="width:100%;"><div class="ui-datatable-tablewrapper"><table role="grid"><thead id="myForm:examDc_head"><tr role="row"><th id="myForm:examDc:columnRefType" class="ui-state-default ui-filter-column" role="columnheader" aria-label="考试" scope="col" style="width:250px!important;text-align: left;"><span class="ui-column-title">考试</span><label id="myForm:examDc:columnRefType:filter_label" for="myForm:examDc:columnRefType:filter" class="ui-helper-hidden">Filter by 考试</label><input id="myForm:examDc:columnRefType:filter" name="myForm:examDc:columnRefType:filter" class="ui-column-filter ui-inputfield ui-inputtext ui-widget ui-state-default ui-corner-all" value="" autocomplete="off" aria-labelledby="myForm:examDc:columnRefType:filter_label" style="width:60%;display:inline;margin-left:10px;" /></th><th id="myForm:examDc:j_idt122" class="ui-state-default" role="columnheader" aria-label="评分类型" scope="col" style="text-align: center;"><span class="ui-column-title">评分类型</span></th><th id="myForm:examDc:j_idt126" class="ui-state-default" role="columnheader" aria-label="考试时长" scope="col" style="width:80px!important;text-align: center;"><span class="ui-column-title">考试时长</span></th><th id="myForm:examDc:j_idt135" class="ui-state-default" role="columnheader" aria-label="题目" scope="col" style="width:180px!important;text-align: center;"><span class="ui-column-title">题目</span></th><th id="myForm:examDc:j_idt153" class="ui-state-default normalFont" role="columnheader" aria-label="开始考试" scope="col" style="text-align: center;width:100px;"><span class="ui-column-title">开始考试</span></th></tr></thead><tbody id="myForm:examDc_data" class="ui-datatable-data ui-widget-content"><tr data-ri="0" class="ui-widget-content ui-datatable-even" role="row"><td role="gridcell" style="width:250px!important;text-align: left;"><span class="headLine2">习思想综合评价</span><br /><span class="tip">开放时间：2025-12-15 00:00</span><br /><span class="tip">结束时间：2025-12-25 23:59</span></td><td role="gridcell" style="text-align: center;"><span class="tip">人工评分</span><br /></td><td role="gridcell" style="width:80px!important;text-align: center;"><span class="tip">60分钟</span><br /></td><td role="gridcell" style="width:180px!important;text-align: center;"><table class="threadColumn special1 special2" cellpadding="0" cellspacing="0" style="text-align: center;">
<tbody>
<tr>
<td><span class="tip">第一部分：1</span></td>
</tr>
</tbody>
</table>
</td><td role="gridcell" style="text-align: center;width:100px;" class="normalFont">未开放<br/></td></tr><tr data-ri="1" class="ui-widget-content ui-datatable-odd" role="row"><td role="gridcell" style="width:250px!important;text-align: left;"><span class="headLine2">习思想第一单元作业</span><br /><span class="tip">开放时间：2025-10-21 00:00</span><br /><span class="tip">结束时间：2025-10-31 23:59</span></td><td role="gridcell" style="text-align: center;"><span class="tip">智能评分</span><br /></td><td role="gridcell" style="width:80px!important;text-align: center;"><span class="tip">30分钟</span><br /></td><td role="gridcell" style="width:180px!important;text-align: center;"><table class="threadColumn special1 special2" cellpadding="0" cellspacing="0" style="text-align: center;">
<tbody>
<tr>
<td><span class="tip">单选题：10</span></td>
<td><span class="tip">多选题：5</span></td>
</tr>
<tr>
<td><span class="tip">判断题：5</span></td>
</tr>
</tbody>
</table>
</td><td role="gridcell" style="text-align: center;width:100px;" class="normalFont">未开放<br/></td></tr><tr data-ri="2" class="ui-widget-content ui-datatable-even" role="row"><td role="gridcell" style="width:250px!important;text-align: left;"><span class="headLine2">形势与政策课程论文</span><br /><span class="tip">开放时间：2025-12-08 00:00</span><br /><span class="tip">结束时间：2026-01-18 23:59</span></td><td role="gridcell" style="text-align: center;"><span class="tip">人工评分</span><br /></td><td role="gridcell" style="width:80px!important;text-align: center;"><span class="tip">60分钟</span><br /></td><td role="gridcell" style="width:180px!important;text-align: center;"><table class="threadColumn special1 special2" cellpadding="0" cellspacing="0" style="text-align: center;">
<tbody>
<tr>
<td><span class="tip">第一部分：1</span></td>
</tr>
</tbody>
</table>
</td><td role="gridcell" style="text-align: center;width:100px;" class="normalFont">超过允许参加的最大次数</td></tr><tr data-ri="3" class="ui-widget-content ui-datatable-odd" role="row"><td role="gridcell" style="width:250px!important;text-align: left;"><span class="headLine2">形势与政策综合评价</span><br /><span class="tip">开放时间：2025-12-08 00:00</span><br /><span class="tip">结束时间：2026-01-18 23:59</span></td><td role="gridcell" style="text-align: center;"><span class="tip">人工评分</span><br /></td><td role="gridcell" style="width:80px!important;text-align: center;"><span class="tip">60分钟</span><br /></td><td role="gridcell" style="width:180px!important;text-align: center;"><table class="threadColumn special1 special2" cellpadding="0" cellspacing="0" style="text-align: center;">
<tbody>
<tr>
<td><span class="tip">第一部分：1</span></td>
</tr>
</tbody>
</table>
</td><td role="gridcell" style="text-align: center;width:100px;" class="normalFont">超过允许参加的最大次数</td></tr><tr data-ri="4" class="ui-widget-content ui-datatable-even" role="row"><td role="gridcell" style="width:250px!important;text-align: left;"><span class="headLine2">习思想课程论文</span><br /><span class="tip">开放时间：2025-12-15 00:00</span><br /><span class="tip">结束时间：2025-12-25 23:59</span></td><td role="gridcell" style="text-align: center;"><span class="tip">人工评分</span><br /></td><td role="gridcell" style="width:80px!important;text-align: center;"><span class="tip">60分钟</span><br /></td><td role="gridcell" style="width:180px!important;text-align: center;"><table class="threadColumn special1 special2" cellpadding="0" cellspacing="0" style="text-align: center;">
<tbody>
<tr>
<td><span class="tip">第一部分：1</span></td>
</tr>
</tbody>
</table>
</td><td role="gridcell" style="text-align: center;width:100px;" class="normalFont">未开放<br/></td></tr><tr data-ri="5" class="ui-widget-content ui-datatable-odd" role="row"><td role="gridcell" style="width:250px!important;text-align: left;"><span class="headLine2">习思想第二单元作业</span><br /><span class="tip">开放时间：2025-10-21 00:00</span><br /><span class="tip">结束时间：2025-10-31 23:59</span></td><td role="gridcell" style="text-align: center;"><span class="tip">智能评分</span><br /></td><td role="gridcell" style="width:80px!important;text-align: center;"><span class="tip">30分钟</span><br /></td><td role="gridcell" style="width:180px!important;text-align: center;"><table class="threadColumn special1 special2" cellpadding="0" cellspacing="0" style="text-align: center;">
<tbody>
<tr>
<td><span class="tip">单选题：10</span></td>
<td><span class="tip">多选题：5</span></td>
</tr>
<tr>
<td><span class="tip">判断题：5</span></td>
</tr>
</tbody>
</table>
</td><td role="gridcell" style="text-align: center;width:100px;" class="normalFont">未开放<br/></td></tr><tr data-ri="6" class="ui-widget-content ui-datatable-even" role="row"><td role="gridcell" style="width:250px!important;text-align: left;"><span class="headLine2">习思想第三单元作业</span><br /><span class="tip">开放时间：2025-11-10 00:00</span><br /><span class="tip">结束时间：2025-11-21 23:59</span></td><td role="gridcell" style="text-align: center;"><span class="tip">智能评分</span><br /></td><td role="gridcell" style="width:80px!important;text-align: center;"><span class="tip">30分钟</span><br /></td><td role="gridcell" style="width:180px!important;text-align: center;"><table class="threadColumn special1 special2" cellpadding="0" cellspacing="0" style="text-align: center;">
<tbody>
<tr>
<td><span class="tip">单选题：10</span></td>
<td><span class="tip">多选题：5</span></td>
</tr>
<tr>
<td><span class="tip">判断题：5</span></td>
</tr>
</tbody>
</table>
</td><td role="gridcell" style="text-align: center;width:100px;" class="normalFont">未开放<br/>超过允许参加的最大次数</td></tr><tr data-ri="7" class="ui-widget-content ui-datatable-odd" role="row"><td role="gridcell" style="width:250px!important;text-align: left;"><span class="headLine2">习思想第四单元作业</span><br /><span class="tip">开放时间：2025-11-10 00:00</span><br /><span class="tip">结束时间：2025-11-21 23:59</span></td><td role="gridcell" style="text-align: center;"><span class="tip">智能评分</span><br /></td><td role="gridcell" style="width:80px!important;text-align: center;"><span class="tip">30分钟</span><br /></td><td role="gridcell" style="width:180px!important;text-align: center;"><table class="threadColumn special1 special2" cellpadding="0" cellspacing="0" style="text-align: center;">
<tbody>
<tr>
<td><span class="tip">单选题：10</span></td>
<td><span class="tip">多选题：5</span></td>
</tr>
<tr>
<td><span class="tip">判断题：5</span></td>
</tr>
</tbody>
</table>
</td><td role="gridcell" style="text-align: center;width:100px;" class="normalFont">未开放<br/>超过允许参加的最大次数</td></tr><tr data-ri="8" class="ui-widget-content ui-datatable-even" role="row"><td role="gridcell" style="width:250px!important;text-align: left;"><span class="headLine2">习思想期末考试</span><br /><span class="tip">开放时间：2026-01-11 19:10</span><br /><span class="tip">结束时间：2026-01-11 20:25</span></td><td role="gridcell" style="text-align: center;"><span class="tip">智能评分</span><br /></td><td role="gridcell" style="width:80px!important;text-align: center;"><span class="tip">50分钟</span><br /></td><td role="gridcell" style="width:180px!important;text-align: center;"><table class="threadColumn special1 special2" cellpadding="0" cellspacing="0" style="text-align: center;">
<tbody>
<tr>
<td><span class="tip">单选题：60</span></td>
<td><span class="tip">多选题：10</span></td>
</tr>
<tr>
<td><span class="tip">判断题：10</span></td>
</tr>
</tbody>
</table>
</td><td role="gridcell" style="text-align: center;width:100px;" class="normalFont">未开放<br/>超过允许参加的最大次数</td></tr></tbody></table></div><div id="myForm:examDc_paginator_bottom" class="ui-paginator ui-paginator-bottom ui-widget-header ui-corner-bottom" role="navigation" aria-label="Pagination"><a href="#" class="ui-paginator-first ui-state-default ui-corner-all ui-state-disabled" aria-label="First Page" tabindex="-1"><span class="ui-icon ui-icon-seek-first">F</span></a><a href="#" class="ui-paginator-prev ui-state-default ui-corner-all ui-state-disabled" aria-label="Previous Page" tabindex="-1"><span class="ui-icon ui-icon-seek-prev">P</span></a><span class="ui-paginator-pages"><a class="ui-paginator-page ui-state-default ui-state-active ui-corner-all" tabindex="0" href="#">1</a></span><a href="#" class="ui-paginator-next ui-state-default ui-corner-all ui-state-disabled" aria-label="Next Page" tabindex="-1"><span class="ui-icon ui-icon-seek-next">N</span></a><a href="#" class="ui-paginator-last ui-state-default ui-corner-all ui-state-disabled" aria-label="Last Page" tabindex="-1"><span class="ui-icon ui-icon-seek-end">E</span></a></div></div><script id="myForm:examDc_s" type="text/javascript">$(function(){PrimeFaces.cw("DataTable","widget_myForm_examDc",{id:"myForm:examDc",paginator:{id:['myForm:examDc_paginator_bottom'],rows:10,rowCount:9,page:0,currentPageTemplate:'({currentPage} of {totalPages})'},filter:true,groupColumnIndexes:[]});});</script></div></div><script id="myForm:mainPanel_s" type="text/javascript">PrimeFaces.cw("Panel","widget_myForm_mainPanel",{id:"myForm:mainPanel"});</script>

                    <br />
                </div>
            </div>
            <div id="mainBottomDiv" style="">
                <div style="width:1000px;margin: 0 auto;border: 0px solid red;"><div id="myForm:j_idt172" class="ui-panel ui-widget ui-widget-content ui-corner-all" style="width:100%;margin:3px 0px 3px 0px!important;padding: 0px!important;border:0px solid #e5e5e5;background: transparent;" data-widget="widget_myForm_j_idt172"><div id="myForm:j_idt172_content" class="ui-panel-content ui-widget-content"><span class="headLine2" style="margin-left: 15px;">友情链接</span><hr id="myForm:j_idt174" class="ui-separator ui-state-default ui-corner-all" /><table style="margin-left: 10px;width: 100%;">
<tbody>
<tr>
<td><a href="http://www.wbdwl.com" target="_blank" class="notice">无标度网络科技</a></td>
</tr>
</tbody>
</table>
</div></div><script id="myForm:j_idt172_s" type="text/javascript">PrimeFaces.cw("Panel","widget_myForm_j_idt172",{id:"myForm:j_idt172"});</script><div id="myForm:j_idt178" class="ui-panel ui-widget ui-widget-content ui-corner-all" style="width:100%;border:0px solid #e5e5e5;background: transparent;" data-widget="widget_myForm_j_idt178"><div id="myForm:j_idt178_content" class="ui-panel-content ui-widget-content">
            <div>
                <table align="center" style="text-align: center; width: 99%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td align="center"><span class="normalFont">版权所有 &copy; 2012-2025 南京林业大学马克思主义学院  技术支持：优学教育科技</span>

                            <br /><span class="normalFont">电话：025-68224709</span>
                            <br />
                            <span class="normalFont">
                                本系统建议在正式考试时使用<a target="_blank" href="https://www.google.com/intl/zh-CN/chrome/browser/" class="notice">Chrome</a>或<a target="_blank" href="http://www.firefox.com.cn/" class="notice">FireFox</a>等高性能浏览器！  
                            </span>
                        </td>
                    </tr>
                </table>
            </div></div></div><script id="myForm:j_idt178_s" type="text/javascript">PrimeFaces.cw("Panel","widget_myForm_j_idt178",{id:"myForm:j_idt178"});</script><div id="myForm:ajaxStatusPanel" style="width:64px;height:64px;position:fixed;right:5px;bottom:5px;z-index: 100"><div id="myForm:ajaxStatusPanel_start" style="display:none"><img id="myForm:j_idt184" src="/resources/images/loading.gif?pfdrid_c=true" alt="" style="" /></div><div id="myForm:ajaxStatusPanel_complete" style="display:none"></div></div><script id="myForm:ajaxStatusPanel_s" type="text/javascript">$(function(){PrimeFaces.cw("AjaxStatus","ajaxStatusPanel",{id:"myForm:ajaxStatusPanel"});});</script>
                </div>
            </div><span id="myForm:j_idt187"></span><script id="myForm:j_idt187_s" type="text/javascript">$(function(){PrimeFaces.cw("Growl","widget_myForm_j_idt187",{id:"myForm:j_idt187",sticky:false,life:6000,escape:true,keepAlive:false,msgs:[]});});</script><input type="hidden" name="javax.faces.ViewState" id="j_id1:javax.faces.ViewState:0" value="-278325818279417138:7654194475685284598" autocomplete="off" />
</form>
            <script type="text/javascript" src="/resources/jquery.Sonline.2.0/js/jquery.Sonline.js"></script>
            <script type="text/javascript">
                var open1=false;
                if (open1) {
                    $(function() {
                        $().Sonline({
                            Position: "left", //left或right
                            Top: 180, //顶部距离，默认200px
                            Width: 151, //顶部距离，默认200px
                            Style: 3, //图标的显示风格共6种风格，默认显示第一种：1
                            Effect: true, //滚动或者固定两种方式，布尔值：true或false
                            DefaultsOpen: false, //默认展开：true,默认收缩：false
                            Tel: "400 007 8605 ", //其它信息图片等
                            Qqlist: "754600590|QQ客服,192773394|QQ客服,2073219188|值班QQ", //多个QQ用','隔开，QQ和客服名用'|'隔开
                            Qunlist: "",
                            Wwlist: "lteb2002:m2|旺旺客服,lteb2002:m3|旺旺客服,lteb2002|意见建议"
                        });
                    });
                }
            </script>
        <script type="text/javascript">
            //蝙蝠在线考试系统，技术支持：成都无标度网络科技有限公司，网址：http://www.wbdwl.com。
        </script></body>
</html>



注意综合评价和课程论文要忽略掉！这个只能手动完成！