/* ALLOCATE MINIMUM NUMBER OF PAGES:

Given number of pages in n different books and m students. The books are arranged in ascending order of number of pages. Every student is assigned to read some consecutive books. The task is to assign books in such a way that the maximum number of pages assigned to a student is minimum.

Example :

Input : pages[] = {12, 34, 67, 90}
        m = 2
Output : 113
Explanation:
There are 2 number of students. Books can be distributed 
in following fashion : 
  1) [12] and [34, 67, 90]
      Max number of pages is allocated to student 
      2 with 34 + 67 + 90 = 191 pages
  2) [12, 34] and [67, 90]
      Max number of pages is allocated to student
      2 with 67 + 90 = 157 pages 
  3) [12, 34, 67] and [90]
      Max number of pages is allocated to student 
      1 with 12 + 34 + 67 = 113 pages

Of the 3 cases, Option 3 has the minimum pages = 113. 

-----***** MOST IMPORTANT QUESTION *****-----

*/

// plz check out video once

/* 
Related Problems For Practice :

Level : Hard

Book Allocation Problem (GFG)
Aggressive cow (spoj)
Prata and roti (spoj)
EKO (spoj)
Google kickstart A Q-3 2020
Painter Partition Problem

+ Below Leetcode Problems
1482 Minimum Number of Days to Make m Bouquets
1283 Find the Smallest Divisor Given a Threshold
1231 Divide Chocolate
1011 Capacity To Ship Packages In N Days
875 Koko Eating Bananas
Minimize 
774 Max Distance to Gas Station
410 Split Array Largest Sum

*/


/*
#include<bits/stdc++.h>
using namespace std ;

bool isvalid(int arr[], int n , int x , int mx) {
    int count = 1;
    int sum = 0;
    for (int i= 0 ; i < n ; i++) {
        sum += arr[i];
        if (sum > mx) {
            count ++;
            sum = arr[i];
        }
        if (count > x) {
            return false;
        }
    }
    return true;
}


int main ()
{

    int n;
    cin >> n;
    int arr[n];
    for(int i=0; i< n; i++) {
        cin>>arr[i];
    }

    int x;
    cin>>x;
    int ans = -1;
    int start = *max_element(arr,arr+n);
    int sum = 0;
    for(int i=0;i<n;i++){
        sum+=arr[i];
    }
    int end =sum; 
    if ( n < x) {
        cout<< -1;
    }
    while(start<=end) {
        int mid = start + (end-start) / 2;
        if( isvalid(arr,n,x, mid ) == true) {  // compare this IMP step
            ans = mid;
            end = mid -1;
        }
        else
            start = mid + 1;
    }
    cout<< ans;

}

*/

#include<bits/stdc++.h>
using namespace std;

bool isvalid(int arr[],int n,int k,int mx){
    int student = 1;
    int sum =0;
    for(int i=0;i<n;i++){
        sum += arr[i];
        if(sum > mx){
            student++;
            sum = arr[i];
        }
        if(student > k) return false;
    }
    return true;
}

int solve(int arr[],int n,int k){
    if(k > n) return -1;
    int ans = -1;
    int start = *max_element(arr,arr+n);
    int sum=0;
    for(int i=0;i<n;i++) {
        sum+=arr[i];
    }
    int end = sum;
    while(start<=end){
        int mid =start + (end - start) / 2;
        if(isvalid(arr,n,k,mid) == true){
            ans = mid;
            end = mid -1;
        }
        else 
            start = mid + 1;
    }
    return ans;
}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    int k;
    cin>>k;
    cout<<solve(arr,n,k);
}