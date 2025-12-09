## Running the Load Test for Evaluation of Scalability and Distributed Performance (standalone vs sharded cluster deployment)

This Locust load test suite designed to benchmark **standalone** and **sharded cluster** MongoDB architectures.

---

### **1 Install dependencies**

See README.MD under root folder

## **2.1 Run the Load Test**

Use:

```
locust -f mixed_blog_user_locust_test.py --host http://localhost:8000
```

Where it simulates a **real blog workload**.

---

## **2.2 Prepare test data (automatic)**

When you start Locust, the script automatically:

- Inserts test users
- Inserts test blogs
- Inserts test comments

---

## 3 Open the Locust UI

Go to: http://localhost:8089
