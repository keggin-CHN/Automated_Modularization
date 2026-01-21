// ==UserScript==
// @name         南林马院平时作业自动答题助手
// @namespace    http://tampermonkey.net/
// @version      2.2
// @description  利用Report页面获取答案，支持题库累积、导入、多格式导出、清空。适配PrimeFaces动态ID。
// @author       Keggin
// @match        http://202.119.208.106/talk/ExamCase*General.jspx*
// @match        http://202.119.208.106/talk/ExamCaseReport*General.jspx*
// @match        http://202.119.208.106/talk/Default.jspx
// @match        http://202.119.208.57/talk/ExamCase*General.jspx*
// @match        http://202.119.208.57/talk/ExamCaseReport*General.jspx*
// @match        http://202.119.208.57/talk/Default.jspx
// @match        http://223.2.96.5:8080/talk/ExamCase*General.jspx*
// @match        http://223.2.96.5:8080/talk/ExamCaseReport*General.jspx*
// @match        http://223.2.96.5:8080/talk/Default.jspx
// @match        http://202.119.208.28/talk/ExamCase*General.jspx*
// @match        http://202.119.208.28/talk/ExamCaseReport*General.jspx*
// @match        http://202.119.208.28/talk/Default.jspx
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_deleteValue
// @grant        window.close
// ==/UserScript==

(function() {
    'use strict';

    const href = window.location.href;
    const isReportPage = href.includes('ExamCaseReportGeneral');
    const isExamPage = href.includes('ExamCaseGeneral') && !isReportPage;
    const isDefaultPage = href.includes('Default.jspx');

    const ANSWER_KEY = 'examAnswers';
    const GLOBAL_Q_BANK = 'globalQuestionBank';

    function getBank() {
        const bankRaw = GM_getValue(GLOBAL_Q_BANK, '{}');
        let bank = {};
        try {
            bank = JSON.parse(bankRaw);
        } catch (e) {
            console.error('解析题库失败', e);
        }
        return bank;
    }
    function cleanText(text) {
        if (!text) return "";
        return text.trim();
    }

    function getCourseName() {
        let courseName = "未知课程";
        const titleText = document.title;
        const tdElements = document.querySelectorAll('td');
        for (let td of tdElements) {
            if (td.textContent.includes('考试名称：')) {
                courseName = td.textContent.replace('考试名称：', '').trim();
                return courseName; 
            }
        }

        const keywords = {
            "毛概": "毛概", "纲要": "纲要", "原理": "马原", "形策": "形策",
            "习概": "习概", "习思想": "习概", "思法": "思法", "心健": "心健",
            "近代史": "纲要"
        };
        for (const key in keywords) {
            if (titleText.includes(key)) {
                courseName = keywords[key];
                break;
            }
        }
        return courseName;
    }

    function categorizeBank(bank) {
        const categories = { single: {}, multi: {}, judge: {} };
        for (const question in bank) {
            const data = bank[question];
            let answerStr = (typeof data === 'object' && data.answer) ? data.answer : data;

            if (answerStr === '正确' || answerStr === '错误') {
                categories.judge[question] = data;
            } else if (answerStr && answerStr.length > 1) {
                categories.multi[question] = data;
            } else {
                categories.single[question] = data;
            }
        }
        return categories;
    }

    function downloadFile(filename, content, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function addBankManagerPanel(topPosition = '100px') {
        const panel = document.createElement('div');
        panel.style.cssText = `position: fixed; top: ${topPosition}; right: 20px; z-index: 9998; background: white; border: 1px solid #ccc; border-radius: 8px; padding: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); display: flex; flex-direction: column; gap: 10px; font-family: sans-serif;`;

        const createButton = (text, color, hoverColor) => {
            const button = document.createElement('button');
            button.textContent = text;
            button.style.cssText = `padding: 10px 15px; background: ${color}; color: white; border: none; border-radius: 5px; font-size: 13px; font-weight: bold; cursor: pointer; transition: background 0.2s;`;
            button.onmouseover = () => button.style.background = hoverColor;
            button.onmouseout = () => button.style.background = color;
            return button;
        };

        const viewButton = createButton('👁️ 查看题库状态', '#0984e3', '#74b9ff');
        viewButton.onclick = function() {
            const count = Object.keys(getBank()).length;
            alert(`当前题库共有: ${count} 道题`);
        };

        const exportJSONButton = createButton('💾 导出 JSON', '#6c5ce7', '#a29bfe');
        exportJSONButton.onclick = function() {
            const bank = getBank();
            if (Object.keys(bank).length === 0) return alert('题库为空！');
            downloadFile('题库_Backup.json', JSON.stringify(bank, null, 2), 'application/json');
        };

        const exportTXTButton = createButton('📄 导出 TXT (适合打印)', '#00cec9', '#81ecec');
        exportTXTButton.onclick = function() {
            const bank = getBank();
            const categories = categorizeBank(bank);
            let content = '';
            const format = (title, data) => {
                let txt = `【${title}】\n\n`;
                let i = 1;
                for (const q in data) {
                    const item = data[q];
                    const ans = item.answer || item;
                    const opts = item.options ? ('\n' + item.options.join('\n')) : '';
                    txt += `${i}. ${q.replace(/^\d+[、.]\s*/, '')}${opts}\n   答案: ${ans}\n\n`;
                    i++;
                }
                return txt;
            };
            content += format('单选题', categories.single);
            content += format('多选题', categories.multi);
            content += format('判断题', categories.judge);
            downloadFile('题库_Print.txt', content, 'text/plain;charset=utf-8');
        };

        const deleteButton = createButton('🗑️ 清空题库', '#e74c3c', '#ff7675');
        deleteButton.onclick = function() {
            if (confirm('确定清空所有题库吗？不可恢复！')) {
                GM_deleteValue(GLOBAL_Q_BANK);
                alert('已清空');
            }
        };

        const importButton = createButton('📥 导入题库', '#f0932b', '#fab1a0');
        importButton.onclick = () => {
             const str = prompt("请粘贴 JSON 内容:");
             if(str) {
                 try {
                     const json = JSON.parse(str);
                     let toMerge = {};
                     if(json.single || json.multi || json.judge) {
                         Object.assign(toMerge, json.single || {}, json.multi || {}, json.judge || {});
                     } else {
                         toMerge = json;
                     }
                     const old = getBank();
                     Object.assign(old, toMerge);
                     GM_setValue(GLOBAL_Q_BANK, JSON.stringify(old));
                     alert(`导入成功，现共有 ${Object.keys(old).length} 题`);
                 } catch(e) {
                     alert("JSON 格式错误");
                 }
             }
        };

        panel.appendChild(viewButton);
        panel.appendChild(importButton);
        panel.appendChild(exportJSONButton);
        panel.appendChild(exportTXTButton);
        panel.appendChild(deleteButton);
        document.body.appendChild(panel);
    }
    if (isReportPage) {
        console.log('检测到Report页面，加载抓取模块...');
        function extractAnswers() {
            const answers = {};
            const panels = document.querySelectorAll('.ui-panel-content');

            if (panels.length === 0) {
                console.error('未找到 .ui-panel-content，页面结构可能已变更');
                return null;
            }

            panels.forEach((panel) => {
                const choiceTitles = panel.querySelectorAll('span.choiceTitle');

                choiceTitles.forEach((titleSpan) => {
                    const rawText = titleSpan.innerText.trim();
                    if (!/^\d+[、.]/.test(rawText)) return;

                    try {
                        const questionText = cleanText(rawText);
                        let correctAnswer = null;
                        let options = [];

                        let nextElem = titleSpan.nextElementSibling;

                        while(nextElem) {
                            if (nextElem.tagName === 'HR') break;
                            if (nextElem.classList.contains('choiceTitle') && /^\d+[、.]/.test(nextElem.innerText)) break;

                            if (nextElem.tagName === 'DIV') {
                                const optSpans = nextElem.querySelectorAll('span.choiceTitle');
                                optSpans.forEach(opt => {
                                    if (!/^\d+[、.]/.test(opt.innerText)) {
                                        options.push(opt.innerText.trim());
                                    }
                                });

                                const answerLabel = nextElem.querySelector('.answer') ||
                                                    Array.from(nextElem.querySelectorAll('span')).find(s => s.innerText.includes('正确答案'));

                                if (answerLabel) {
                                    const greenSpan = nextElem.querySelector('span[style*="color:green"][style*="font-weight: bold"]');
                                    if (greenSpan) {
                                        correctAnswer = greenSpan.innerText.trim();
                                    }
                                }
                            }

                            nextElem = nextElem.nextElementSibling;
                        }


                        if (correctAnswer) {
                            correctAnswer = correctAnswer.replace(/[.\s]/g, '');
                            if (correctAnswer === "true") correctAnswer = "正确";
                            if (correctAnswer === "false") correctAnswer = "错误";

                            answers[questionText] = { answer: correctAnswer, options: options };
                        }

                    } catch (e) {
                        console.error('单题解析出错:', e);
                    }
                });
            });

            console.log(`本次共提取到 ${Object.keys(answers).length} 道题的答案`);
            return answers;
        }

        function addExtractButton() {
            const button = document.createElement('button');
            button.textContent = '🚀 抓取答案并存入题库';
            button.style.cssText = `position: fixed; top: 100px; right: 20px; z-index: 9999; padding: 15px 25px; background: #ff4757; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.3);`;
            button.onclick = function() {
                const courseName = getCourseName();
                const newAnswers = extractAnswers();

                if (!newAnswers || Object.keys(newAnswers).length === 0) {
                    alert('❌ 未能提取到答案！\n请按 F12 打开控制台查看是否有报错。');
                    return;
                }

                const oldBank = getBank();
                const mergedBank = Object.assign(oldBank, newAnswers);

                GM_setValue(GLOBAL_Q_BANK, JSON.stringify(mergedBank));
                GM_setValue(ANSWER_KEY, JSON.stringify(newAnswers));

                alert(`✅ [${courseName}] 提取成功！\n\n本次获取: ${Object.keys(newAnswers).length} 题\n题库总量: ${Object.keys(mergedBank).length} 题\n\n即将尝试跳转回考试页面...`);

                const examUrl = window.location.href.replace('ExamCaseReportGeneral', 'ExamCaseGeneral');
                window.location.href = examUrl;
            };
            document.body.appendChild(button);
        }

        addExtractButton();
        addBankManagerPanel('170px');

    }


    else if (isExamPage) {
        console.log('检测到答题页面');

        function fillAnswers(answers) {
            let filledCount = 0;
            const titleElements = document.querySelectorAll('span.choiceTitle');

            titleElements.forEach((element) => {
                const questionText = cleanText(element.innerText);
                if (questionText && answers[questionText]) {

                    const answerData = answers[questionText];
                    let correctAns = (typeof answerData === 'object') ? answerData.answer : answerData;

                    console.log(`匹配到题目: ${questionText.substring(0,10)}... 答案: ${correctAns}`);

                    let nextElem = element.nextElementSibling;
                    let foundOptionsArea = false;


                    for(let i=0; i<5; i++) {
                        if(!nextElem) break;
                        const labels = nextElem.querySelectorAll('label');
                        if (labels.length > 0) {
                            foundOptionsArea = true;
                            labels.forEach(label => {
                                const optText = label.innerText.trim(); 
                                const optChar = optText.charAt(0);


                                let shouldClick = false;

                                if (['正确', '错误'].includes(correctAns)) {
                                    if (optText.includes(correctAns)) shouldClick = true;
                                } else {
                                    if (correctAns.includes(optChar)) shouldClick = true;
                                }
                                const inputId = label.getAttribute('for');
                                const input = document.getElementById(inputId);
                                const isChecked = input ? input.checked : false;
                                if (shouldClick && !isChecked) {
                                    label.click();
                                    filledCount++;
                                }
                            });
                            break;
                        }
                        nextElem = nextElem.nextElementSibling;
                    }
                }
            });
            return filledCount;
        }

        function addFillButton(answers) {
            const btn = document.createElement('button');
            const total = Object.keys(answers).length;
            btn.textContent = `✅ 自动填充 (题库: ${total}题)`;
            btn.style.cssText = `position: fixed; top: 100px; right: 20px; z-index: 9999; padding: 15px 25px; background: #2ecc71; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.3);`;

            btn.onclick = function() {
                const count = fillAnswers(answers);
                if (count > 0) {
                    alert(`已为您点击了 ${count} 个选项。\n请务必人工检查一遍再提交！`);
                } else {
                    alert(`未能匹配到任何题目。\n可能是题目文本有细微差异或题库不包含当前题目。`);
                }
            };
            document.body.appendChild(btn);
        }
        const bank = getBank();
        const tempRaw = GM_getValue(ANSWER_KEY);
        if (tempRaw) {
            try {
                const temp = JSON.parse(tempRaw);
                Object.assign(bank, temp);
                console.log('合并了临时抓取的答案');
            } catch(e){}
        }

        if (Object.keys(bank).length > 0) {
            addFillButton(bank);
        } else {
            console.log('题库为空，不显示填充按钮');
        }

    }
    else if (isDefaultPage) {
        addBankManagerPanel('100px');
    }

})();