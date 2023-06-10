//input : 10
//1 -1 2 4 7 -8 11 2 -3 4 3
//3
//output : -1 -1 0 -8 -8 -8 -3 -3

#include<iostream>
#include<algorithm>
#include<bits/stdc++.h>
using namespace std;

int main()
{
    int n;
  cin>>n;
  int arr[n];
  for(int i=0;i<n;i++)
    {
        cin>> arr[i];
    }
  int k;//block size
  cin>>k;

  /*int flag;

     for (int i = 0; i<(n-k+1); i++)          
    {
        flag = false;
 
        // traverse through the current window
        for (int j = 0; j<k; j++)
        {
            // if a negative integer is found, then
            // it is the first negative integer for
            // current window. Print it, set the flag
            // and break
            if (arr[i+j] < 0)
            {
                cout << arr[i+j] << " ";
                flag = true;
                break;
            }
        }
         
        // if the current window does not
        // contain a negative integer
        if (!flag)
            cout << "0" << " ";
    }
  
   */ long long j=0,i=0;
    vector<int>v;
    queue<int> prb;
   while(j<n)
    {
        if(arr[j] < 0) {
                prb.push(arr[j]);
            }
       
        if( j-i+1 < k ) { 
            j++;
        }

        else if(j-i+1 == k) 
        {
            if (prb.size() == 0) {
               // cout<<"0 ";
               v.push_back(0);
            }
            else {
                //cout<< prb.front()<<" "; 
                v.push_back(prb.front());
                if( arr[i] == prb.front()) {
                    //prb.pop_back(arr[i]);  //we have to remove the first value in vector
                    prb.pop(); // in queue pop will always first inserted element
                }            
            }
            i++;
            j++;
            
        }
        
    }
    for(int i=0;i<v.size();i++){
        cout<<v[i]<<" ";
    }
}

