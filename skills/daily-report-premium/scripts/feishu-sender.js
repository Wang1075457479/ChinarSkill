#!/usr/bin/env node
/**
 * 飞书视频上传和发送工具
 * 
 * 流程：
 * 1. 上传视频到飞书云盘，获取 file_key
 * 2. 使用 file_key 发送视频消息
 */

const fs = require('fs');
const path = require('path');

/**
 * 上传文件到飞书云盘并获取 file_key
 * 注意：此功能需要飞书 API 的 tenant_access_token
 * 
 * @param {string} filePath - 本地文件路径
 * @param {string} token - 飞书 tenant_access_token
 * @returns {Promise<string>} file_key
 */
async function uploadToFeishuDrive(filePath, token) {
    const axios = require('axios');
    const FormData = require('form-data');
    
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    form.append('file_type', 'mp4');
    form.append('file_name', path.basename(filePath));
    
    try {
        const response = await axios.post(
            'https://open.feishu.cn/open-apis/drive/v1/medias/upload_all',
            form,
            {
                headers: {
                    ...form.getHeaders(),
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        
        if (response.data.code === 0) {
            return response.data.data.file_key;
        } else {
            throw new Error(`上传失败: ${response.data.msg}`);
        }
    } catch (error) {
        console.error('上传视频失败:', error.message);
        throw error;
    }
}

/**
 * 发送视频消息到飞书
 * 
 * @param {string} fileKey - 飞书 file_key
 * @param {string} openId - 用户 open_id
 * @param {string} token - 飞书 tenant_access_token
 * @param {string} message - 附带文字消息
 */
async function sendVideoMessage(fileKey, openId, token, message = '') {
    const axios = require('axios');
    
    const content = {
        file_key: fileKey
    };
    
    if (message) {
        // 先发送文字消息
        await sendTextMessage(message, openId, token);
    }
    
    try {
        const response = await axios.post(
            'https://open.feishu.cn/open-apis/im/v1/messages',
            {
                receive_id: openId,
                msg_type: 'media',
                content: JSON.stringify(content)
            },
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                params: {
                    receive_id_type: 'open_id'
                }
            }
        );
        
        if (response.data.code === 0) {
            console.log('✅ 视频发送成功');
            return response.data.data;
        } else {
            throw new Error(`发送失败: ${response.data.msg}`);
        }
    } catch (error) {
        console.error('发送视频失败:', error.message);
        throw error;
    }
}

/**
 * 发送文字消息
 */
async function sendTextMessage(text, openId, token) {
    const axios = require('axios');
    
    try {
        const response = await axios.post(
            'https://open.feishu.cn/open-apis/im/v1/messages',
            {
                receive_id: openId,
                msg_type: 'text',
                content: JSON.stringify({ text })
            },
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                params: {
                    receive_id_type: 'open_id'
                }
            }
        );
        
        return response.data;
    } catch (error) {
        console.error('发送文字消息失败:', error.message);
        throw error;
    }
}

/**
 * 完整的视频发送流程
 * 
 * @param {string} videoPath - 视频文件路径
 * @param {string} openId - 用户 open_id (如 ou_ceb518d7c2b872e794f0c9374889b36d)
 * @param {string} token - 飞书 tenant_access_token
 * @param {string} message - 附带消息
 */
async function sendVideoToFeishu(videoPath, openId, token, message = '') {
    console.log('🚀 开始发送视频到飞书...\n');
    
    // 检查文件
    if (!fs.existsSync(videoPath)) {
        throw new Error(`文件不存在: ${videoPath}`);
    }
    
    const stats = fs.statSync(videoPath);
    console.log(`📁 文件: ${path.basename(videoPath)}`);
    console.log(`📊 大小: ${(stats.size / 1024 / 1024).toFixed(2)} MB\n`);
    
    // Step 1: 上传视频到飞书云盘
    console.log('📤 Step 1: 上传视频到飞书云盘...');
    const fileKey = await uploadToFeishuDrive(videoPath, token);
    console.log(`✅ 上传成功，file_key: ${fileKey}\n`);
    
    // Step 2: 发送视频消息
    console.log('📨 Step 2: 发送视频消息...');
    await sendVideoMessage(fileKey, openId, token, message);
    
    console.log('\n🎉 完成！视频已发送到飞书');
}

// 如果直接运行
if (require.main === module) {
    const videoPath = process.argv[2];
    const openId = process.argv[3] || 'ou_ceb518d7c2b872e794f0c9374889b36d';
    const token = process.argv[4];
    const message = process.argv[5] || '主人，今日系统运转情报已送达。';
    
    if (!videoPath || !token) {
        console.log('用法: node feishu-sender.js <视频路径> [用户open_id] <token> [消息]');
        console.log('示例: node feishu-sender.js /path/to/video.mp4 ou_xxx t-xxx "日报来了"');
        process.exit(1);
    }
    
    sendVideoToFeishu(videoPath, openId, token, message)
        .catch(console.error);
}

module.exports = {
    uploadToFeishuDrive,
    sendVideoMessage,
    sendVideoToFeishu
};
