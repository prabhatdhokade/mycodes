#include<bits/stdc++.h>
// input 1 3 -1 -3 5 3 6 7
// 3
// output 3 3 5 5 6 7

using namespace std;

/*
int main()
{
  int N;
  cin>>N;
  int arr[N];
  for(int i=0;i<N;i++)
    {
        cin>>arr[i];
    }
  int K;//blcok size 
  cin>>K;


int i=0,j=0;
int max= 0;
list<int> l;


while( j< N) 
{
    
    while(l.size() > 0 && l.back() < arr[j]) {  // while loop is important here just check ones
        l.pop_back();  // we are poping it until lists get empty or first element is greater than the next elemnt 
    }
    
    l.push_back(arr[j]);
 
    if(j-i+1 < K) {
        j++;
    }

    else if ( j-i+1 == K)
    {
        cout<<l.front()<<" ";
        if( arr[i] == l.front()) {
            l.pop_front();
        }

        i++;
        j++;
    }
}
} */

vector<int> solve(int n,int arr[],int k){
    int i=0;
    int j=0;
    deque<int>q;    // use only deque or list beacuse at q.back() and at gives wrong output sso this is the correct ans;
    vector<int>v;  // dont use queue it dosn't give correct op sometimes

    while(j<n){
        while(q.size() >0 && q.back() < arr[j]) { q.pop_back(); } // catch
       
        q.push_back(arr[j]);

        if(j-i+1 < k) j++;

        else if( j-i+1 == k){
            v.push_back(q.front());
            if(q.front() == arr[i]){
                q.pop_front();   // always remeber in queue the  first is always first out
            }
            i++;
            j++;
        } 
    }
    return v;
}


int main() {
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
    cin>>arr[i];
    }
    int k;
    cin>>k;
    vector<int>v;
    v = solve(n,arr,k);
    for(auto it=v.begin(); it!=v.end();it++) {
        cout<<*it<<" ";
    }
}