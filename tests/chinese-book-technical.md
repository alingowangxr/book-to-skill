# JavaScript 核心概念（測試版）

**作者**：測試作者 | **版本**：1.0

---

## 目錄

- [第一章 變數與作用域](#第一章-變數與作用域)
- [第二章 閉包](#第二章-閉包)
- [第三章 Promise 非同步](#第三章-promise-非同步)
- [第四章 原型鏈](#第四章-原型鏈)
- [第五章 模組化](#第五章-模組化)

---

## 第一章 變數與作用域

JavaScript 有三種變數宣告方式：`var`、`let` 和 `const`。

### var 的作用域

```javascript
function example() {
    var x = 10;
    if (true) {
        var x = 20;  // 同一個變數
        console.log(x); // 20
    }
    console.log(x); // 20
}
```

### let 和 const 的區塊作用域

```javascript
function example() {
    let x = 10;
    if (true) {
        let y = 20;  // 區塊作用域
        console.log(y); // 20
    }
    // console.log(y); // ReferenceError
}
```

## 第二章 閉包

閉包是函數與其詞法環境的組合。

```javascript
function createCounter() {
    let count = 0;
    return function() {
        count += 1;
        return count;
    };
}

const counter = createCounter();
console.log(counter()); // 1
console.log(counter()); // 2
```

**使用場景**：資料封裝、工廠函數、事件處理。

## 第三章 Promise 非同步

Promise 用於處理非同步操作。

```javascript
function fetchData(url) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve(`數據來自 ${url}`);
        }, 1000);
    });
}

async function main() {
    try {
        const data = await fetchData('/api/users');
        console.log(data);
    } catch (error) {
        console.error('請求失敗：', error);
    }
}
```

## 第四章 原型鏈

JavaScript 透過原型鏈實現繼承。

```javascript
function Animal(name) {
    this.name = name;
}

Animal.prototype.speak = function() {
    console.log(`${this.name} 發出聲音`);
};

function Dog(name) {
    Animal.call(this, name);
}

Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;

Dog.prototype.bark = function() {
    console.log(`${this.name} 汪汪叫`);
};

const dog = new Dog('小白');
dog.speak(); // 小白 發出聲音
dog.bark();  // 小白 汪汪叫
```

## 第五章 模組化

ES6 引入了原生模組系統。

```javascript
// math.js
export function add(a, b) {
    return a + b;
}

export function multiply(a, b) {
    return a * b;
}

// app.js
import { add, multiply } from './math.js';

console.log(add(2, 3));      // 5
console.log(multiply(2, 3)); // 6
```

### 設計模式比較

| 模式 | 用途 | 範例 |
|------|------|------|
| 單例模式 | 確保只有一個實例 | `new Promise()` |
| 觀察者模式 | 事件驅動 | `addEventListener` |
| 工廠模式 | 建立物件 | `createElement` |
| 策略模式 | 動態演算法 | 表單驗證 |

### 參考資料

- MDN Web Docs
- You Don't Know JS
- JavaScript: The Good Parts
